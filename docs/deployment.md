# Deployment

This reference build is a single Python process for the API and a Streamlit process for the UI. The UI calls the graph in-process unless `COPILOT_API_URL` is set.

## Local

```powershell
cd $HOME\ai-security-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m backend.main
```

In a second terminal:

```powershell
streamlit run frontend/app.py
```

The API listens on http://127.0.0.1:8000. The UI listens on http://127.0.0.1:8501.

## Docker

```powershell
docker build -t security-copilot .
docker run --rm -p 8000:8000 -e HOST=0.0.0.0 security-copilot
```

`docker compose up --build` starts the API and the UI. The UI container sets `COPILOT_API_URL=http://api:8000`.

## CI

GitHub Actions installs dependencies, runs `pytest`, and fails the job on a test failure. The recall assertion is one of those tests.

## Configuration

| Variable | Purpose |
| --- | --- |
| `HOST`, `PORT` | API bind address |
| `COPILOT_API_URL` | If set, Streamlit calls the API instead of the in-process graph |
| `CHROMA_PATH` | Optional dense index |
| `GEMINI_API_KEY` | Reserved. The reference narrative does not call Gemini |

Do not send production alerts to a deployment that has no authentication.
