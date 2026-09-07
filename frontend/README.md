# Sovereign AI Frontend

Vanilla HTML/CSS/JS workbench for SIH PS 26117 (MRPL).

## Open locally

From this folder:

```bash
python -m http.server 8080
```

Then visit `http://localhost:8080/login.html`.

Demo login: `admin` / `admin123`

## Demo path

Login → Dashboard → AI Workbench → attach files → ask about C-204 bearing → live trace → answer, confidence, Why This Result?, sources → “Generate a technical maintenance report.” → Audit Logs.

## Backend

Set `window.SOVEREIGN_USE_MOCK = false` and `window.SOVEREIGN_API_BASE` before the scripts when the Python API is ready. Mock implementations live in `js/mock-api.js`.
