from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from fastapi_stellody.app_factory import create_app
from fastapi_stellody.dependencies import get_mailer
from fastapi_stellody.mail import (
    _get_env_bool,
    _get_env_bool_with_fallback,
    _get_env_int,
    _get_env_required,
    build_mailer_from_env,
)


def test_app_module_exports_asgi_app() -> None:
    # Cover [`fastapi_stellody/app.py`](fastapi_stellody/app.py:1).
    module = importlib.import_module("fastapi_stellody.app")
    assert getattr(module, "app") is not None


def test_mail_env_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("X_REQUIRED", raising=False)
    with pytest.raises(RuntimeError):
        _get_env_required("X_REQUIRED")

    monkeypatch.setenv("X_REQUIRED", "")
    with pytest.raises(RuntimeError):
        _get_env_required("X_REQUIRED")

    monkeypatch.setenv("X_REQUIRED", "  ok  ")
    assert _get_env_required("X_REQUIRED") == "  ok  "

    monkeypatch.delenv("X_BOOL", raising=False)
    assert _get_env_bool("X_BOOL", default=True) is True

    monkeypatch.setenv("X_BOOL", "true")
    assert _get_env_bool("X_BOOL", default=False) is True

    monkeypatch.setenv("X_BOOL", "0")
    assert _get_env_bool("X_BOOL", default=True) is False

    monkeypatch.delenv("P", raising=False)
    monkeypatch.delenv("F", raising=False)
    assert _get_env_bool_with_fallback("P", "F", default=True) is True

    monkeypatch.setenv("F", "true")
    assert _get_env_bool_with_fallback("P", "F", default=False) is True

    monkeypatch.setenv("P", "0")
    assert _get_env_bool_with_fallback("P", "F", default=True) is False

    monkeypatch.delenv("X_INT", raising=False)
    assert _get_env_int("X_INT", default=587) == 587

    monkeypatch.setenv("X_INT", "")
    assert _get_env_int("X_INT", default=2525) == 2525

    monkeypatch.setenv("X_INT", "123")
    assert _get_env_int("X_INT", default=1) == 123


def test_build_mailer_from_env_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAIL_USERNAME", "user")
    monkeypatch.setenv("MAIL_PASSWORD", "pass")
    monkeypatch.setenv("MAIL_FROM", "no-reply@example.com")
    monkeypatch.setenv("MAIL_SERVER", "smtp.example.com")
    monkeypatch.setenv("MAIL_PORT", "587")
    monkeypatch.setenv("MAIL_TLS", "true")
    monkeypatch.setenv("MAIL_SSL", "false")
    monkeypatch.setenv("CONTACT_RECIPIENT", "recipient@example.com")

    mailer = build_mailer_from_env()
    assert mailer.contact_recipient == "recipient@example.com"
    assert mailer.fastmail is not None


def test_startup_initializes_mailer_when_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAIL_USERNAME", "user")
    monkeypatch.setenv("MAIL_PASSWORD", "pass")
    monkeypatch.setenv("MAIL_FROM", "no-reply@example.com")
    monkeypatch.setenv("MAIL_SERVER", "smtp.example.com")
    monkeypatch.setenv("MAIL_PORT", "587")
    monkeypatch.setenv("MAIL_TLS", "true")
    monkeypatch.setenv("MAIL_SSL", "false")
    monkeypatch.setenv("CONTACT_RECIPIENT", "recipient@example.com")

    app = create_app()
    assert getattr(app.state, "mailer") is None

    with TestClient(app) as client:
        # Trigger at least one request to ensure lifespan is active.
        response = client.get("/")
        assert response.status_code == 200

    assert getattr(app.state, "mailer") is not None


def test_startup_does_not_override_existing_mailer(monkeypatch: pytest.MonkeyPatch) -> None:
    # If tests or other code set app.state.mailer before startup, startup should not override it.
    monkeypatch.setenv("MAIL_USERNAME", "user")
    monkeypatch.setenv("MAIL_PASSWORD", "pass")
    monkeypatch.setenv("MAIL_FROM", "no-reply@example.com")
    monkeypatch.setenv("MAIL_SERVER", "smtp.example.com")
    monkeypatch.setenv("MAIL_PORT", "587")
    monkeypatch.setenv("MAIL_TLS", "true")
    monkeypatch.setenv("MAIL_SSL", "false")
    monkeypatch.setenv("CONTACT_RECIPIENT", "recipient@example.com")

    app = create_app()
    sentinel = object()
    app.state.mailer = sentinel

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200

    assert app.state.mailer is sentinel


def test_get_mailer_raises_when_not_configured() -> None:
    class _State:
        mailer = None

    class _App:
        state = _State()

    class _Request:
        app = _App()

    with pytest.raises(RuntimeError):
        get_mailer(_Request())

