from __future__ import annotations

import os
from dataclasses import dataclass

from fastapi_mail import ConnectionConfig, FastMail


def _get_env_required(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Configure it in Render (Environment) before deploying."
        )
    return value


def _get_env_bool(name: str, *, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _get_env_bool_with_fallback(
    primary: str, fallback: str, *, default: bool
) -> bool:
    """Read a boolean env var, with a compatibility fallback name.

    Render config in this repo uses MAIL_TLS / MAIL_SSL, but newer fastapi-mail
    expects MAIL_STARTTLS / MAIL_SSL_TLS.
    """

    if os.environ.get(primary) is not None:
        return _get_env_bool(primary, default=default)
    if os.environ.get(fallback) is not None:
        return _get_env_bool(fallback, default=default)
    return default


def _get_env_int(name: str, *, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return int(raw)


@dataclass(frozen=True)
class Mailer:
    """Application-wide mail sender.

    Keep recipient + SMTP config in environment variables. Do not expose in templates.
    """

    fastmail: FastMail
    contact_recipient: str


def build_mailer_from_env() -> Mailer:
    """Create the shared FastMail instance from environment variables.

    This is meant to run once at app startup.
    """

    mail_from = _get_env_required("MAIL_FROM")

    # Map repo env vars (MAIL_TLS / MAIL_SSL) onto fastapi-mail's expected names
    # (MAIL_STARTTLS / MAIL_SSL_TLS).
    mail_starttls = _get_env_bool_with_fallback(
        "MAIL_STARTTLS",
        "MAIL_TLS",
        default=True,
    )
    mail_ssl_tls = _get_env_bool_with_fallback(
        "MAIL_SSL_TLS",
        "MAIL_SSL",
        default=False,
    )

    config = ConnectionConfig(
        MAIL_USERNAME=_get_env_required("MAIL_USERNAME"),
        MAIL_PASSWORD=_get_env_required("MAIL_PASSWORD"),
        MAIL_FROM=mail_from,
        MAIL_FROM_NAME=os.environ.get("MAIL_FROM_NAME", "Stellody Contact"),
        MAIL_SERVER=_get_env_required("MAIL_SERVER"),
        MAIL_PORT=_get_env_int("MAIL_PORT", default=587),
        MAIL_STARTTLS=mail_starttls,
        MAIL_SSL_TLS=mail_ssl_tls,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    return Mailer(
        fastmail=FastMail(config),
        contact_recipient=_get_env_required("CONTACT_RECIPIENT"),
    )

