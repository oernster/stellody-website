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


def test_canonical_and_open_graph_tags_are_present(client: TestClient) -> None:
    response = client.get("/pricing")
    assert response.status_code == 200
    html = response.text

    assert '<link rel="canonical" href="https://stellody.com/pricing"' in html
    assert '<meta property="og:title"' in html
    assert '<meta property="og:description"' in html
    assert '<meta property="og:image" content="https://stellody.com/static/stellody-options-2.png"' in html
    assert '<meta name="twitter:card" content="summary_large_image"' in html
    assert '<meta name="twitter:site" content="@stellody"' in html


def test_cart_and_checkout_are_noindex_nofollow(client: TestClient) -> None:
    for path in ("/cart", "/checkout"):
        response = client.get(path)
        assert response.status_code == 200
        assert '<meta name="robots" content="noindex,nofollow"' in response.text


def test_robots_txt_and_sitemap_xml(client: TestClient) -> None:
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    assert "User-agent: *" in response.text
    assert "Disallow: /cart" in response.text
    assert "Disallow: /checkout" in response.text
    assert "Sitemap: https://stellody.com/sitemap.xml" in response.text

    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert "application/xml" in response.headers.get("content-type", "")
    xml = response.text

    assert "https://stellody.com/" in xml
    assert "https://stellody.com/pricing" in xml
    assert "https://stellody.com/contact" in xml
    assert "https://stellody.com/cart" not in xml
    assert "https://stellody.com/checkout" not in xml
