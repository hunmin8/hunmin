#!/usr/bin/env python3
"""Wikipedia langlinks → corpus builder.

영문 Wikipedia 페이지 → 한국어 langlink 추출.
NIKL gold 검증용 corpus 자동 생성.

Usage:
    python scripts/build_wiki_corpus.py --category "Capitals_in_Europe" --limit 100
    python scripts/build_wiki_corpus.py --titles paris,berlin,tokyo
    python scripts/build_wiki_corpus.py --from-list scripts/seed_titles.txt
"""
from __future__ import annotations
import argparse, json, re, sys, time
import urllib.request, urllib.parse

UA = 'hunmin-corpus-builder/1.0 (https://github.com/meshpop/hunmin)'
API = 'https://en.wikipedia.org/w/api.php'


def _http(url, retries=3, backoff=2):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            return json.loads(urllib.request.urlopen(req, timeout=15).read())
        except Exception as e:
            last = e
            if '429' in str(e) or '503' in str(e):
                wait = backoff * (i + 1)
                time.sleep(wait)
            else:
                break
    raise last


def fetch_langlinks(titles, target='ko'):
    """50개 batch → 한국어 매핑 반환."""
    if not titles: return {}
    params = {
        'action': 'query',
        'titles': '|'.join(titles[:50]),
        'prop': 'langlinks', 'lllang': target,
        'lllimit': 'max', 'format': 'json',
    }
    data = _http(API + '?' + urllib.parse.urlencode(params))
    out = {}
    for pid, page in data.get('query', {}).get('pages', {}).items():
        title = page.get('title')
        for ll in page.get('langlinks', []):
            if ll['lang'] == target:
                out[title] = ll['*']
                break
    return out


def fetch_category(cat, limit=500):
    """카테고리 멤버 article 제목."""
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f'Category:{cat}',
        'cmlimit': min(limit, 500), 'format': 'json',
    }
    data = _http(API + '?' + urllib.parse.urlencode(params))
    return [m['title'] for m in data.get('query', {}).get('categorymembers', [])
            if m.get('ns') == 0]


def clean_ko(ko):
    """한국어 제목 정리 — disambiguation 등 제거."""
    ko = re.sub(r'\s*\([^)]*\)\s*$', '', ko).strip()
    ko = re.sub(r'\s+', ' ', ko)
    return ko


def looks_korean(text):
    """순수 한국어인지 (한글 + space + 일부 punctuation)."""
    if not text: return False
    has_hangul = any(0xAC00 <= ord(c) <= 0xD7A3 for c in text)
    has_latin = any(c.isascii() and c.isalpha() for c in text)
    return has_hangul and not has_latin


def harvest(titles, lang='en', target='ko', delay=1.0):
    """대량 영한 매핑 추출."""
    results = []
    for i in range(0, len(titles), 50):
        chunk = titles[i:i+50]
        try:
            ko_map = fetch_langlinks(chunk, target=target)
        except Exception as e:
            print(f'  ERR batch {i}: {e}', file=sys.stderr)
            time.sleep(delay * 5)
            continue
        for en, ko in ko_map.items():
            ko_clean = clean_ko(ko)
            if not looks_korean(ko_clean):
                continue
            en_clean = en.replace('_', ' ')
            results.append((en_clean, ko_clean, lang, 'wiki'))
        time.sleep(delay)  # rate limit 안전
        sys.stderr.write(f'  ... {i+len(chunk)}/{len(titles)}\n')
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--category', help='Wikipedia 카테고리 이름 (e.g., Capitals_in_Europe)')
    ap.add_argument('--titles', help='쉼표 구분 영문 제목 list')
    ap.add_argument('--from-list', help='파일 (한 줄당 영문 제목)')
    ap.add_argument('--target-lang', default='ko', help='target lang (default ko)')
    ap.add_argument('--source-lang', default='en', help='source lang code for output (default en)')
    ap.add_argument('--limit', type=int, default=500)
    ap.add_argument('--delay', type=float, default=1.0, help='Sec between batches')
    ap.add_argument('--output', '-o', default=None, help='Output TSV path (default stdout)')
    args = ap.parse_args()

    titles = []
    if args.category:
        titles = fetch_category(args.category, limit=args.limit)
        print(f'  Category "{args.category}" → {len(titles)} titles', file=sys.stderr)
    if args.titles:
        titles += [t.strip() for t in args.titles.split(',') if t.strip()]
    if args.from_list:
        with open(args.from_list, encoding='utf-8') as f:
            titles += [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not titles:
        ap.error('--category, --titles, --from-list 중 하나 필요')

    pairs = harvest(titles[:args.limit], lang=args.source_lang,
                     target=args.target_lang, delay=args.delay)

    out = sys.stdout if args.output is None else open(args.output, 'w', encoding='utf-8')
    out.write(f'# Wikipedia langlinks corpus ({args.source_lang} → {args.target_lang})\n')
    out.write('# Format: word<TAB>expected_korean<TAB>lang<TAB>category\n')
    for w, k, l, c in pairs:
        out.write(f'{w}\t{k}\t{l}\t{c}\n')
    if args.output:
        out.close()
    print(f'saved {len(pairs)} pairs', file=sys.stderr)


if __name__ == '__main__':
    main()
