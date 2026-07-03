# <img width="48" height="48" alt="Stellody favicon" src="fastapi_stellody/static/favicon.ico" /> Stellody

A minimal placeholder website for Stellody: a single server-rendered page showing a
sunny landscape (fields and trees) and a "coming soon" message.

---

## About

This is a deliberately small FastAPI app. It serves one page from a Jinja2 template
and the favicon from `/static`. The sunny scene is drawn inline as SVG, so the page has
no external asset dependencies.

It is intended as a stand-in while the full Stellody site is rebuilt. It is NOT a
marketing site, a store, or a contact/download service; that functionality was removed.

---

## Stack

| Concern    | Choice                          |
| ---------- | ------------------------------- |
| Web        | FastAPI + Jinja2 (server-side)  |
| Server     | Uvicorn / ASGI                  |
| Deployment | Render (`requirements.txt`)     |
| Tests      | pytest, 100% coverage gate      |

---

## Local development

Install dependencies:

```bash
pip install -r fastapi_stellody/requirements.txt
pip install -r requirements-dev.txt
```

Run via the shim entrypoint:

```bash
python site.py
```

Dev mode (auto-reload):

```bash
python site.py --reload
```

Then open http://127.0.0.1:8004

Alternate (run Uvicorn directly):

```bash
uvicorn fastapi_stellody.app:app --reload
```

---

## Tests (100% coverage)

```bash
python -m pytest -v --cov
```

## Formatting & linting

```bash
python -m black .
python -m flake8 .
```

---

## Project layout

- [`site.py`](site.py:1) - shim entrypoint (`python site.py`)
- [`fastapi_stellody/app.py`](fastapi_stellody/app.py:1) - ASGI app export (`app = create_app()`)
- [`fastapi_stellody/app_factory.py`](fastapi_stellody/app_factory.py:1) - FastAPI factory + the single placeholder route
- [`fastapi_stellody/paths.py`](fastapi_stellody/paths.py:1) - templates/static path resolution
- [`fastapi_stellody/templates/index.html`](fastapi_stellody/templates/index.html:1) - the placeholder page (inline SVG scene)
- [`fastapi_stellody/static/`](fastapi_stellody/static/favicon.ico:1) - favicon
- [`tests/`](tests/test_app_routes.py:1) - test suite

---

## License

LGPL-3.0. See [`LICENSE`](LICENSE:1).
