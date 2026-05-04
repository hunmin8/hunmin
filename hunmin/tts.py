"""TTS integration — UHPS-full / Hangul → 음성 (audio).

전략: 외국어 단어를 hunmin으로 한글로 변환 후 Korean TTS 엔진 사용.

Backends (선택적 deps):
    - gTTS (pip install gtts) — Google TTS, online
    - edge-tts (pip install edge-tts) — Microsoft Edge TTS, online (좋은 한국어 음성)
    - pyttsx3 (pip install pyttsx3) — offline (시스템 TTS)

Usage:
    from hunmin import transcribe
    from hunmin.tts import speak, save_mp3

    hangul = transcribe('Mozart', 'de')   # → '모차르트'
    save_mp3(hangul, 'mozart.mp3')         # 저장
    speak(hangul)                           # 즉시 재생 (deps 따라)
"""
from __future__ import annotations
import os
import tempfile


def save_mp3(text: str, output_path: str, *, backend: str = 'auto',
             voice: str | None = None, lang: str = 'ko') -> str:
    """Hangul 텍스트 → MP3 파일.

    Args:
        text: 한글 텍스트 (transcribe() 결과).
        output_path: 출력 mp3 경로.
        backend: 'auto' / 'gtts' / 'edge' / 'pyttsx3'.
        voice: edge-tts voice ID (예: 'ko-KR-SunHiNeural').
        lang: gTTS lang code (default 'ko').

    Returns:
        저장된 파일 경로.

    Raises:
        ImportError: 선택한 backend의 deps 미설치.
    """
    if backend == 'auto':
        for b in ('edge', 'gtts', 'pyttsx3'):
            try:
                return save_mp3(text, output_path, backend=b, voice=voice, lang=lang)
            except ImportError:
                continue
        raise ImportError(
            "TTS backend 없음. 선택 설치:\n"
            "  pip install gtts        # 간단, online\n"
            "  pip install edge-tts    # 고품질 한국어, online\n"
            "  pip install pyttsx3     # offline (system TTS)\n"
        )

    if backend == 'gtts':
        try:
            from gtts import gTTS
        except ImportError:
            raise ImportError("pip install gtts")
        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        return output_path

    if backend == 'edge':
        try:
            import edge_tts
            import asyncio
        except ImportError:
            raise ImportError("pip install edge-tts")
        v = voice or 'ko-KR-SunHiNeural'
        async def _gen():
            communicate = edge_tts.Communicate(text, v)
            await communicate.save(output_path)
        asyncio.run(_gen())
        return output_path

    if backend == 'pyttsx3':
        try:
            import pyttsx3
        except ImportError:
            raise ImportError("pip install pyttsx3")
        engine = pyttsx3.init()
        # offline TTS는 직접 mp3 저장 어려움 — wav으로 저장 후 conversion 필요
        wav_path = output_path.replace('.mp3', '.wav')
        engine.save_to_file(text, wav_path)
        engine.runAndWait()
        return wav_path

    raise ValueError(f'Unknown backend: {backend!r}')


def speak(text: str, *, backend: str = 'auto', voice: str | None = None,
          lang: str = 'ko') -> None:
    """Hangul → 즉시 재생 (cross-platform).

    임시 mp3 파일을 만든 뒤 시스템 player (afplay/aplay/start 등)로 재생.
    """
    suffix = '.mp3' if backend != 'pyttsx3' else '.wav'
    fd, tmp = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        save_mp3(text, tmp, backend=backend, voice=voice, lang=lang)
        _play_audio(tmp)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _play_audio(path: str) -> None:
    """Cross-platform audio playback."""
    import sys, subprocess
    if sys.platform == 'darwin':
        subprocess.run(['afplay', path], check=False)
    elif sys.platform.startswith('linux'):
        # Try common players
        for cmd in ('mpg123', 'mpv', 'ffplay', 'aplay'):
            try:
                subprocess.run([cmd, path], check=False, stderr=subprocess.DEVNULL)
                return
            except FileNotFoundError:
                continue
    elif sys.platform == 'win32':
        os.startfile(path)


def transcribe_and_speak(text: str, lang: str, **kwargs) -> str:
    """One-shot: text → 한글 → 음성.

    Args:
        text: 외국어 단어/문장.
        lang: 언어 코드.
        **kwargs: speak()에 전달.

    Returns:
        변환된 한글 (재생도 됨).

    Examples:
        >>> from hunmin.tts import transcribe_and_speak  # doctest: +SKIP
        >>> transcribe_and_speak('Mozart', 'de')  # doctest: +SKIP
        '모차르트'
    """
    from . import transcribe
    hangul = transcribe(text, lang)
    speak(hangul, **kwargs)
    return hangul
