# Hunmin VS Code Extension

선택한 텍스트를 한글 발음 표기로 변환.

## 기능

- **Transcribe selection**: 선택 텍스트 → 한글 (NIKL 표기)
- **UHPS-full**: 옛한글 보존 변환
- **Reverse romanize**: 한글 → 영문 발음 (Revised Romanization)
- **Show views**: 모든 모드 한 번에 panel에 표시

## 사전 준비

Hunmin REST API 서버 실행:

```bash
pip install hunmin[cjk] fastapi uvicorn
uvicorn hunmin.server:app --port 8000
```

또는 Docker:

```bash
docker run -p 8000:8000 hunmin/api
```

## 설치 (개발용)

```bash
cd vscode-extension
npm install
npm run compile
# F5 키로 Extension Host 디버깅 모드 실행
```

## 키 바인딩

- `Cmd+Alt+H` (Mac) / `Ctrl+Alt+H` (Win/Linux): 선택 텍스트 변환
- 우클릭 메뉴: Hunmin 그룹

## 설정

```json
{
  "hunmin.defaultLang": "en",
  "hunmin.serverUrl": "http://localhost:8000"
}
```

## 사용 예

1. `Hello world` 선택
2. `Cmd+Alt+H`
3. 언어 선택 ("en")
4. → `헬로 월드` 로 치환됨

## License

MIT
