# <img width="48" height="48" alt="Stellody favicon" src="fastapi_stellody/static/favicon.ico" /> Stellody

A small multi-page marketing site built with FastAPI and Jinja2 templates  ~  designed for fast iteration and simple local development.

---

## About

This project serves the Stellody website experience  ~  a lightweight FastAPI app that renders server-side pages from Jinja templates and serves static assets (CSS/JS/favicon).

Pages are implemented as small, focused routers (see [`fastapi_stellody/routers/pages.py`](fastapi_stellody/routers/pages.py:1)) and rendered using templates in [`fastapi_stellody/templates/`](fastapi_stellody/templates/base.html:1).

---

## Features

- FastAPI backend with Jinja2 server-side rendering
- Multi-page routes (home, pricing, licenses, FAQ, contact, cart/checkout)
- Static assets served from `/static` (CSS/JS/favicon)
- Release-based download redirects under `/downloads/*` (no binaries stored/built/proxied by the app)
- Simple contact form handler (placeholder redirect)
- Automated tests with 100% Python coverage via [`pytest.ini`](pytest.ini:1) / [`.coveragerc`](.coveragerc:1)

---

## Local Development

Install dependencies:

```bash
pip install -r fastapi_stellody/requirements.txt
```

Install dev/test tooling:

```bash
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

Then open:

- http://127.0.0.1:8000

### Session configuration (cart)

The cart uses cookie-backed sessions via Starlette's session middleware. For local development you can rely
on a default, but for production set a strong secret:

```bash
set SESSION_SECRET=replace-with-a-long-random-value
```

### Release-based downloads (installer redirects)

Installer artifacts are not stored in this repository. Instead, the site exposes stable URLs under
`/downloads/*` that redirect (HTTP 307) directly to GitHub Release assets.

The release tag is controlled by `TAG_RELEASED_VERSION` (recommended for Render). If unset, the
application defaults deterministically to `v1.3.0`.

Examples:

- `/downloads/stellody.dmg`
- `/downloads/stellody.flatpak`
- `/downloads/stellody_installer.exe`

### Alternate: run Uvicorn directly

```bash
uvicorn fastapi_stellody.app:app --reload
```

---

## Tests (100% coverage)

The test suite is designed to reach and enforce 100% coverage of the Python code in this repository.

Run tests with verbose output and coverage:

```bash
python -m pytest -v --cov
```

Equivalent (wrapper) command, if you prefer running tests via `python`:

```bash
python -m tests -v --cov
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
- [`fastapi_stellody/app_factory.py`](fastapi_stellody/app_factory.py:1) - FastAPI app factory + router wiring
- [`fastapi_stellody/routers/`](fastapi_stellody/routers/__init__.py:1) - route modules (home/pages/contact/cart/checkout)
- [`fastapi_stellody/templates/`](fastapi_stellody/templates/base.html:1) - Jinja templates
- [`fastapi_stellody/static/`](fastapi_stellody/static/app.js:1) - static assets
- [`fastapi_stellody/requirements.txt`](fastapi_stellody/requirements.txt:1) - Python dependencies
- [`requirements-dev.txt`](requirements-dev.txt:1) - dev/test dependencies (pytest/coverage/black/flake8)
- [`tests/`](tests/test_app_routes.py:1) - test suite

