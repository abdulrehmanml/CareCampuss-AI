"""Message drafting shared by the follow-up and outreach agents.
Privacy: only a {name} placeholder is sent to Gemini; the real name is filled in locally."""
from utils import llm


def rewrite(base: str, lang: str, name: str):
    """Return (text, source) where source is 'gemini' or 'template'."""
    if llm.available():
        try:
            out = llm.generate(
                f"Rewrite this hospital message as a warm, respectful WhatsApp message in {lang}, "
                f"max 40 words, no medical advice or claims. Keep the token {{name}} exactly as written, "
                f"and keep dates and reasons:\n{base}").strip()
            if "{name}" in out:
                return out.replace("{name}", name), "gemini"
        except Exception:
            pass
    return base.replace("{name}", name), "template"
