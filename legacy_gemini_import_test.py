"""Kontrak dependency untuk entrypoint Streamlit AeroVulpis lama."""

from pathlib import Path

from google import genai


source = Path(__file__).with_name("streamlit_app.py").read_text(encoding="utf-8")
assert genai.Client is not None
assert "from google import genai" in source
assert "import google.generativeai" not in source
assert "google-genai" in Path(__file__).with_name("requirements.txt").read_text(encoding="utf-8")
print("legacy_gemini_import_test_ok")
