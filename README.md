# <img width="48" height="48" alt="Stellody favicon" src="fastapi_stellody/static/favicon.ico" /> Stellody

A small multi-page marketing site built with FastAPI and Jinja2 templates  ~  designed for fast iteration and simple local development.

---

## About

This project serves the Stellody website experience  ~  a lightweight FastAPI app that renders server-side pages from Jinja templates and serves static assets (CSS/JS/favicon).

Pages are implemented as straightforward route handlers in [`fastapi_stellody/app.py`](fastapi_stellody/app.py:1) and rendered using templates in [`fastapi_stellody/templates/`](fastapi_stellody/templates/base.html:1).

---

## Features

- FastAPI backend with Jinja2 server-side rendering
- Multi-page routes (home, pricing, licenses, FAQ, contact, cart/checkout)
- Static assets served from `/static` (CSS/JS/favicon)
- Simple contact form handler (placeholder redirect)

---

## Local Development

Install dependencies:

```bash
pip install -r fastapi_stellody/requirements.txt
```

Run via the shim entrypoint:

```bash
python site.py
```

Dev mode (auto-reload):

```bash
python site.py --reload
```

Then open:

- http://127.0.0.1:8000

### Alternate: run Uvicorn directly

```bash
uvicorn fastapi_stellody.app:app --reload
```

---

## Project layout

- [`site.py`](site.py:1) — shim entrypoint (`python site.py`)
- [`fastapi_stellody/app.py`](fastapi_stellody/app.py:1) — FastAPI app + routes
- [`fastapi_stellody/templates/`](fastapi_stellody/templates/base.html:1) — Jinja templates
- [`fastapi_stellody/static/`](fastapi_stellody/static/app.js:1) — static assets
- [`fastapi_stellody/requirements.txt`](fastapi_stellody/requirements.txt:1) — Python dependencies

