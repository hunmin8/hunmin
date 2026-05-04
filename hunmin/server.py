"""Hunmin REST API server (FastAPI).

Run:
    pip install fastapi uvicorn
    uvicorn hunmin.server:app --host 0.0.0.0 --port 8000

Endpoints:
    GET  /health                       — health check
    GET  /version                      — package version
    GET  /supported                    — supported lang codes
    POST /transcribe                   — main endpoint
    POST /views                        — multi-view
    POST /reverse                      — Hangul → roman/ipa
    GET  /docs                         — OpenAPI Swagger UI
"""
from __future__ import annotations
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError as e:
    raise ImportError("REST API needs fastapi: pip install fastapi uvicorn") from e

from . import (
    __version__, transcribe, views as _views, supported_languages,
    to_romanization, transcribe_cache_info,
)

app = FastAPI(
    title="Hunmin API",
    description="Universal phonetic Hangul transcription — converts any language to readable Korean Hangul.",
    version=__version__,
)


class TranscribeRequest(BaseModel):
    text: str
    lang: str
    mode: Optional[str] = None
    phonetic: bool = False


class ViewsRequest(BaseModel):
    text: str
    lang: str
    meaning: Optional[str] = None


class ReverseRequest(BaseModel):
    text: str  # Korean Hangul
    system: str = 'rr'  # 'rr' or 'ipa'


@app.get('/health')
def health():
    return {'status': 'ok', 'version': __version__}


@app.get('/version')
def version():
    return {'version': __version__}


@app.get('/supported')
def supported(tier: str = 'all'):
    """Supported language codes."""
    return supported_languages(tier=tier)


@app.post('/transcribe')
def post_transcribe(req: TranscribeRequest):
    """Main transcription endpoint."""
    try:
        out = transcribe(req.text, req.lang, mode=req.mode, phonetic=req.phonetic)
        return {'text': req.text, 'lang': req.lang, 'mode': req.mode, 'output': out}
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=501, detail=f'Missing dependency: {e}')


@app.post('/views')
def post_views(req: ViewsRequest):
    """Multi-view (모든 mode 한 번에)."""
    try:
        return _views(req.text, req.lang, meaning=req.meaning)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/reverse')
def post_reverse(req: ReverseRequest):
    """Hangul → Romanization/IPA."""
    try:
        out = to_romanization(req.text, system=req.system)
        return {'text': req.text, 'system': req.system, 'output': out}
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/cache')
def cache_status():
    """LRU cache status."""
    info = transcribe_cache_info()
    return {
        'hits': info.hits, 'misses': info.misses,
        'maxsize': info.maxsize, 'currsize': info.currsize,
    }
