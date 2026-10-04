"""Gemini access with several key sources and honest error reporting."""
import os
import re
import time
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]
_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY")


def _clean(value):
    return value.strip().strip("\"'").strip() if value else None


def _looks_real(key: str) -> bool:
    return len(key) >= 20 and "your" not in key.lower() and " " not in key


def _read_text(path: Path):
    """Read text saved by Notepad, VS Code or PowerShell (UTF-8, UTF-8 BOM or UTF-16)."""
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="ignore")
    return raw.decode("utf-8-sig", errors="ignore")


def _from_file(path: Path):
    text = _read_text(path)
    if text is None:
        return None
    for name in _NAMES:
        m = re.search(rf"^\s*{name}\s*=\s*(.+?)\s*$", text, re.M | re.I)
        if m:
            return _clean(m.group(1).split(" #")[0])
    m = re.search(r"AIza[0-9A-Za-z_\-]{30,}", text)
    return m.group(0) if m else None


def candidate_files() -> list[Path]:
    seen, out = set(), []
    for p in (APP_DIR / ".streamlit" / "secrets.toml", Path.cwd() / ".streamlit" / "secrets.toml",
              APP_DIR / "secrets.toml", APP_DIR / ".env", Path.cwd() / ".env"):
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def status_hint() -> str:
    """One plain sentence explaining why no key was found."""
    wrong = APP_DIR / ".streamlit" / "secrets.toml.txt"
    if wrong.exists():
        return "Found 'secrets.toml.txt'. Rename it to 'secrets.toml' (remove .txt)."
    main = APP_DIR / ".streamlit" / "secrets.toml"
    if not main.exists():
        return f"File not found: {main}"
    found = _from_file(main)
    if not found:
        return "secrets.toml exists but has no GEMINI_API_KEY line."
    if not _looks_real(found):
        return "secrets.toml still contains placeholder text. Paste your real key."
    return "Key line found but it could not be used."


def _from_st_secrets():
    try:
        for name in _NAMES:
            if st.secrets.get(name):
                return st.secrets.get(name)
    except Exception:
        pass
    return None


def key_info():
    """Return (key, source). Checked in order; placeholders such as 'your-key' are ignored."""
    sources = [
        ("Streamlit secrets", _from_st_secrets),
        ("Environment variable", lambda: os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
    ] + [(".env" if p.name == ".env" else ".streamlit/secrets.toml" if "streamlit" in str(p) else "secrets.toml",
          (lambda p=p: _from_file(p))) for p in candidate_files()]
    for label, getter in sources:
        key = _clean(getter())
        if key and _looks_real(key):
            return key, label
    return None, "not found"


def model() -> str:
    return st.session_state.get("model", MODELS[0])


def available() -> bool:
    return key_info()[0] is not None


def explain(exc: Exception) -> str:
    s, low = str(exc), str(exc).lower()
    if "api key" in low or "api_key_invalid" in low or "permission_denied" in low or "401" in s or "403" in s:
        return "Google rejected this key. Create a new key in AI Studio and make sure it was copied completely."
    if "429" in s or "quota" in low or "resource_exhausted" in low:
        return "Quota or rate limit reached for this key. Wait a minute or try another model."
    if "location is not supported" in low or "failed_precondition" in low:
        return "Google says the Gemini API is not available for this key's location or account. Try another Google account or check AI Studio."
    if "404" in s or "not found" in low:
        return "This model is not available for the key. Pick another model in the Tech panel."
    return f"{type(exc).__name__}: {s[:180]}"


def generate(prompt: str, system: str | None = None, as_json: bool = False) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key_info()[0])
    config = types.GenerateContentConfig(
        system_instruction=system, temperature=0.3,
        response_mime_type="application/json" if as_json else None)
    try:
        return client.models.generate_content(model=model(), contents=prompt, config=config).text
    except Exception as exc:
        st.session_state["llm_error"] = explain(exc)
        raise


def generate_json(prompt: str, system: str | None = None):
    """Return (parsed_dict, raw_text)."""
    import json
    raw = generate(prompt, system, as_json=True)
    match = re.search(r"\{.*\}", raw, re.S)
    return json.loads(match.group(0) if match else raw), raw


def test_connection():
    t = time.perf_counter()
    try:
        out = generate("Reply with the single word OK.").strip()
        st.session_state.pop("llm_error", None)
        st.session_state["llm_verified"] = True
        return True, f"Gemini replied: {out[:40]}", int((time.perf_counter() - t) * 1000)
    except Exception as exc:
        st.session_state["llm_verified"] = False
        return False, explain(exc), int((time.perf_counter() - t) * 1000)
