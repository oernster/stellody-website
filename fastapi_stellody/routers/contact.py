from __future__ import annotations

import json
import logging
import os
import time
import urllib.parse
import urllib.request

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr

from fastapi_stellody.dependencies import get_email_sender, get_renderer
from fastapi_stellody.email_delivery import ResendEmailSender
from fastapi_stellody.rendering import PageRenderer

router = APIRouter()

logger = logging.getLogger(__name__)


TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def _strip_crlf(value: str) -> str:
    # Prevent header injection and keep display values tidy.
    return value.replace("\r", " ").replace("\n", " ").strip()


def _client_ip(request: Request) -> str | None:
    # Prefer Cloudflare-provided client IP when present.
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip
    if request.client is None:
        return None
    return request.client.host


def _turnstile_is_enabled() -> bool:
    # Default: enabled only if both vars are present.
    flag = os.environ.get("TURNSTILE_ENABLED")
    if flag is not None:
        return flag.strip().lower() in {"1", "true", "yes", "on"}
    return bool(
        os.environ.get("TURNSTILE_SITE_KEY") and os.environ.get("TURNSTILE_SECRET_KEY")
    )


def _contact_throttle_enabled() -> bool:
    flag = os.environ.get("CONTACT_THROTTLE_ENABLED")
    if flag is None:
        return False
    return flag.strip().lower() in {"1", "true", "yes", "on"}


def _is_rate_limited(request: Request) -> bool:
    """Lightweight per-process throttling (defense-in-depth).

    Primary rate limiting should be enforced at Cloudflare/WAF edge. This is a
    best-effort fallback to reduce damage if edge rules are misconfigured.

    - 5 requests / minute / IP
    - 50 requests / day / IP

    Notes:
    - In-memory and per-process (not shared across workers/instances)
    - Uses session as a secondary key if IP is missing
    """

    now = time.time()
    ip = _client_ip(request) or f"session:{id(request.session)}"

    # Lazy-init process global buckets.
    buckets = getattr(_is_rate_limited, "_buckets", None)
    if buckets is None:
        buckets = {}
        setattr(_is_rate_limited, "_buckets", buckets)

    minute_key = (ip, int(now // 60))
    day_key = (ip, int(now // 86400))

    minute_count = buckets.get(minute_key, 0) + 1
    day_count = buckets.get(day_key, 0) + 1

    buckets[minute_key] = minute_count
    buckets[day_key] = day_count

    # Opportunistic cleanup: drop the previous minute/day bucket for this IP.
    buckets.pop((ip, int(now // 60) - 1), None)
    buckets.pop((ip, int(now // 86400) - 1), None)

    return minute_count > 5 or day_count > 50


def _verify_turnstile(*, token: str, remote_ip: str | None) -> bool:
    secret = os.environ.get("TURNSTILE_SECRET_KEY")
    if not secret:
        # Misconfiguration: treat as disabled rather than failing closed.
        return True

    payload = {
        "secret": secret,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        TURNSTILE_VERIFY_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
        parsed = json.loads(body)
    except Exception:
        # Network or parsing issue: fail closed (no email), but keep UX silent.
        return False

    return bool(parsed.get("success"))


@router.get("/contact", response_class=HTMLResponse)
async def contact_get(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    # Used for minimum-submit-time validation.
    request.session["contact_form_rendered_at"] = time.time()

    return renderer.render_page(
        template_name="contact.html",
        request=request,
        title="Contact",
        turnstile_site_key=os.environ.get("TURNSTILE_SITE_KEY"),
        turnstile_enabled=_turnstile_is_enabled(),
    )


@router.post("/contact")
async def contact_post(
    request: Request,
    name: str = Form(...),
    email: EmailStr = Form(...),
    # Optional for backwards-compatibility with older templates/tests.
    subject: str | None = Form(None),
    message: str | None = Form(None),
    # Backwards-compatibility for older templates/clients.
    msg: str | None = Form(None),
    # Honeypot field: should remain empty for humans.
    company: str | None = Form(None),
    # Cloudflare Turnstile token field name.
    cf_turnstile_response: str | None = Form(None, alias="cf-turnstile-response"),
    email_sender: ResendEmailSender = Depends(get_email_sender),
):
    """Send contact form submission via Resend.

    - Recipient is configured via CONTACT_RECIPIENT env var (never shown on frontend).
    - Reply-To is set to the submitter's email.
    """

    # Layer 2 (fallback): best-effort throttling (silent).
    # Disabled by default; primary rate limiting should be enforced at Cloudflare.
    if _contact_throttle_enabled() and _is_rate_limited(request):
        return RedirectResponse(url="/contact?sent=1", status_code=303)

    # Layer 3: honeypot.
    if company is not None and company.strip():
        return RedirectResponse(url="/contact?sent=1", status_code=303)

    # Layer 4: minimum submit time (requires prior GET /contact).
    rendered_at = request.session.get("contact_form_rendered_at")
    if rendered_at is not None:
        try:
            elapsed = time.time() - float(rendered_at)
        except Exception:
            elapsed = 0.0
        if elapsed < 3.0:
            return RedirectResponse(url="/contact?sent=1", status_code=303)

    resolved_message = message if message is not None else msg
    if resolved_message is None:
        # Match FastAPI's validation semantics while remaining compatible with older
        # clients.
        raise HTTPException(
            status_code=422,
            detail="Field required: message",
        )

    # Layer 5: input hardening + limits.
    safe_name = _strip_crlf(name)
    resolved_subject = _strip_crlf(subject) if subject is not None else "General contact"
    resolved_message = resolved_message.strip()

    if len(safe_name) > 80:
        return RedirectResponse(url="/contact?sent=1", status_code=303)
    if len(resolved_subject) > 120:
        return RedirectResponse(url="/contact?sent=1", status_code=303)
    if len(resolved_message) > 5000:
        return RedirectResponse(url="/contact?sent=1", status_code=303)

    # Layer 1: Turnstile verification (silent failure).
    if _turnstile_is_enabled():
        if not cf_turnstile_response:
            return RedirectResponse(url="/contact?sent=1", status_code=303)
        ok = _verify_turnstile(
            token=cf_turnstile_response,
            remote_ip=_client_ip(request),
        )
        if not ok:
            return RedirectResponse(url="/contact?sent=1", status_code=303)

    try:
        await email_sender.send_contact_email(
            name=safe_name,
            email=str(email),
            subject=resolved_subject,
            message=resolved_message,
        )
    except Exception as exc:
        # Do not log message contents.
        logger.error(
            "Contact email send failed (%s)",
            type(exc).__name__,
            exc_info=True,
        )
        # Silent failure: do not provide a bot oracle and avoid retry amplification.
        return RedirectResponse(url="/contact?sent=1", status_code=303)

    return RedirectResponse(url="/contact?sent=1", status_code=303)
