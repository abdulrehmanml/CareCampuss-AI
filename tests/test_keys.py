import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import llm  # noqa: E402


def test_reads_key_from_toml_and_env_files(tmp_path):
    toml = tmp_path / "secrets.toml"
    toml.write_text('GEMINI_API_KEY = "AIzaSyExampleExampleExample12345"\n', encoding="utf-8")
    assert llm._from_file(toml) == "AIzaSyExampleExampleExample12345"
    env = tmp_path / ".env"
    env.write_text("GEMINI_API_KEY=AIzaSyExampleExampleExample12345\n", encoding="utf-8")
    assert llm._from_file(env) == "AIzaSyExampleExampleExample12345"


def test_placeholder_is_not_a_real_key():
    assert not llm._looks_real("your-real-key")
    assert llm._looks_real("AIzaSyExampleExampleExample12345")


def test_reads_utf16_file_made_by_powershell(tmp_path):
    f = tmp_path / "secrets.toml"
    f.write_bytes('GEMINI_API_KEY = "AIzaSyExampleExampleExample12345"\r\n'.encode("utf-16"))
    assert llm._from_file(f) == "AIzaSyExampleExampleExample12345"
