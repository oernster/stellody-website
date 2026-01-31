from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient
import pytest


@dataclass(frozen=True)
class PageCase:
    path: str
    expected_title: str


def _assert_html_title(html: str, expected: str) -> None:
    assert f"<title>{expected} | Stellody</title>" in html


def test_all_html_pages_render_with_expected_titles(client: TestClient) -> None:
    cases = (
        PageCase("/", "Home"),
        PageCase("/why-stellody", "Why Stellody?"),
        PageCase("/pricing", "Pricing"),
        PageCase("/pro-license", "Professional License"),
        PageCase("/standard-license", "Standard License"),
        PageCase("/help", "Help!"),
        PageCase("/faq", "FAQ"),
        PageCase("/change-log", "Change-log"),
        PageCase("/contact", "Contact"),
        PageCase("/demo", "Demo License"),
        PageCase("/cart", "Cart"),
        PageCase("/checkout", "Checkout"),
    )

    for case in cases:
        response = client.get(case.path)
        assert response.status_code == 200
        _assert_html_title(response.text, case.expected_title)


def test_cart_flow_add_then_replace_then_clear(client: TestClient) -> None:
    # Starts empty.
    response = client.get("/cart")
    assert response.status_code == 200
    assert "currently empty" in response.text

    # Invalid license types should be ignored (still redirects, but cart stays empty).
    response = client.post(
        "/add-to-cart",
        data={"license_type": "invalid"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/cart"

    response = client.get("/cart")
    assert response.status_code == 200
    assert "currently empty" in response.text

    # Add Standard.
    response = client.post(
        "/add-to-cart",
        data={"license_type": "standard"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/cart"

    response = client.get("/cart")
    assert response.status_code == 200
    assert "Standard License" in response.text
    assert "EXJ35PLE2CTF2" in response.text

    # Replace with Pro.
    response = client.post(
        "/add-to-cart",
        data={"license_type": "pro"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/cart"

    response = client.get("/cart")
    assert response.status_code == 200
    assert "Pro License" in response.text
    assert "AQRY5CDP4Z344" in response.text
    assert "Standard License" not in response.text

    # Clear.
    response = client.post("/cart/clear", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/cart"

    response = client.get("/cart")
    assert response.status_code == 200
    assert "currently empty" in response.text


def test_session_secret_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure we cover the startup validation branch.
    monkeypatch.delenv("SESSION_SECRET", raising=False)

    from fastapi_stellody.app_factory import create_app

    with pytest.raises(RuntimeError, match=r"SESSION_SECRET must be set"):
        create_app()


def test_contact_post_redirects_to_home(client: TestClient) -> None:
    response = client.post(
        "/contact",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "message": "Hello",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/contact?sent=1"

    # Backwards-compatible field name.
    response = client.post(
        "/contact",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "msg": "Hello",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/contact?sent=1"

    # Exercise the handler body for full coverage.
    response = client.post(
        "/contact",
        data={
            "name": "Coverage User",
            "email": "coverage@example.com",
            "message": "Coverage",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    _assert_html_title(response.text, "Contact")
    assert "Thanks" in response.text


def test_contact_post_failure_redirects_to_error(client: TestClient) -> None:
    class _FailingEmailSender:
        async def send_contact_email(self, *_args, **_kwargs) -> None:
            raise RuntimeError("SMTP down")

    client.app.state.email_sender = _FailingEmailSender()

    response = client.post(
        "/contact",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "message": "Hello",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/contact?error=1"

    response = client.post(
        "/contact",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "message": "Hello",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Unable to send right now" in response.text


def test_contact_post_missing_message_returns_422(client: TestClient) -> None:
    response = client.post(
        "/contact",
        data={
            "name": "Test User",
            "email": "test@example.com",
        },
        follow_redirects=False,
    )
    assert response.status_code == 422


def test_static_assets_are_served(client: TestClient) -> None:
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    # Keep assertion minimal and resilient.
    assert "text/css" in response.headers.get("content-type", "")
