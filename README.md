Jewelry App - Python Ready package
==================================
Contents:
- backend/ : FastAPI backend (SQLite). Run locally for testing.
- mobile/  : Kivy mobile client (desktop runnable). Configure API_URL in mobile/app_config.py.
- build/   : buildozer.spec and notes to build Android APK.
- .github/workflows/build-android.yml : GitHub Actions workflow to run Buildozer and upload APK artifact.

Quick local test (no Android build):
1) Backend:
   - python -m venv .venv
   - source .venv/bin/activate   (Windows: .venv\Scripts\activate)
   - pip install -r backend/requirements.txt
   - uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
2) Mobile (desktop):
   - pip install -r mobile/requirements.txt
   - python mobile/main.py
   - Edit mobile/app_config.py to set API_URL to backend host (http://127.0.0.1:8000)

To build Android APK on GitHub Actions:
- Create a GitHub repo and push this project (include hidden .github folder).
- Actions will run and produce APK as artifact.
