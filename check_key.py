"""Check your Gemini key without starting the app.   Run:  python check_key.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import llm  # noqa: E402


def main():
    print("CareCompass AI - Gemini key check\n")
    key, source = llm.key_info()
    if not key:
        print("RESULT: no usable key found.")
        print("Reason:", llm.status_hint())
        print("\nThe key must be saved in this file:")
        print("  ", llm.APP_DIR / ".streamlit" / "secrets.toml")
        print("with exactly one line:")
        print('   GEMINI_API_KEY = "paste-your-key-here"')
        return
    print(f"Key found in: {source} ({key[:4]}...{key[-4:]}, {len(key)} characters)")
    if not key.startswith("AIza"):
        print("Note: AI Studio keys normally start with 'AIza'. Check you copied the key itself.")
    from google import genai

    client = genai.Client(api_key=key)
    for model in llm.MODELS:
        try:
            reply = client.models.generate_content(model=model, contents="Reply with the single word OK.")
            print(f"[PASS] {model}: {reply.text.strip()[:30]}")
            print("\nYour key works. Start the app with:  streamlit run app.py")
            return
        except Exception as exc:
            print(f"[FAIL] {model}: {llm.explain(exc)}")
    print("\nEvery model failed. The messages above are Google's reason.")


main()
