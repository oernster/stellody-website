from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient
import pytest


@dataclass(frozen=True)
class PageCase:
    path: str
    expected_title: str


def _assert_html_title(html: str, expected: str) -> None:
    assert f"<title>{expected}</title>" in html


def _assert_meta_description_present(html: str) -> None:
    assert '<meta name="description"' in html


def test_all_html_pages_render_with_expected_titles(client: TestClient) -> None:
    cases = (
        # Homepage uses an explicit SEO title (not the generic "Home | Stellody").
        PageCase(
            "/", "Stellody | Spotify Playlist Generator for Local and Streaming Music"
        ),
        PageCase("/why-stellody", "Why Stellody? | Stellody"),
        PageCase("/pricing", "Pricing | Stellody"),
        PageCase("/pro-license", "Professional License | Stellody"),
        PageCase("/standard-license", "Standard License | Stellody"),
        PageCase("/help", "Help! | Stellody"),
        PageCase("/faq", "FAQ | Stellody"),
        PageCase("/change-log", "Change-log | Stellody"),
        PageCase("/contact", "Contact | Stellody"),
        PageCase("/demo", "Demo License | Stellody"),
        PageCase("/cart", "Cart | Stellody"),
        PageCase("/checkout", "Checkout | Stellody"),
    )

    for case in cases:
        response = client.get(case.path)
        assert response.status_code == 200
        _assert_html_title(response.text, case.expected_title)
        _assert_meta_description_present(response.text)


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
    _assert_html_title(response.text, "Contact | Stellody")
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


def test_legacy_routes_redirect_as_expected(client: TestClient) -> None:
    # Browsers may request this automatically.
    response = client.get("/favicon.ico", follow_redirects=False)
    assert response.status_code == 308
    assert response.headers["location"] == "/static/favicon.ico"

    # Backwards-compatible product link.
    for path in ("/product/stellody", "/product/stellody/"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 308
        assert response.headers["location"] == "/pricing"


def test_download_redirects_to_github_release_assets(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Ensure a developer/CI environment variable doesn't override the deterministic default.
    monkeypatch.delenv("TAG_RELEASED_VERSION", raising=False)

    base = "https://github.com/oernster/stellody-website/releases/download/v1.4.0"

    cases = (
        ("/downloads/stellody.dmg", f"{base}/stellody.dmg"),
        ("/downloads/stellody.flatpak", f"{base}/stellody.flatpak"),
        ("/downloads/stellody_installer.exe", f"{base}/stellody_installer.exe"),
    )

    for path, expected_location in cases:
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


def test_download_redirect_uses_tag_released_version_env_var(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TAG_RELEASED_VERSION", "v9.9.9")
    response = client.get("/downloads/stellody.dmg", follow_redirects=False)
    assert response.status_code == 307
    assert (
        response.headers["location"]
        == "https://github.com/oernster/stellody-website/releases/download/v9.9.9/stellody.dmg"
    )


def test_canonical_and_open_graph_tags_are_present(client: TestClient) -> None:
    response = client.get("/pricing")
    assert response.status_code == 200
    html = response.text

    assert '<link rel="canonical" href="https://stellody.com/pricing"' in html
    assert '<meta property="og:title"' in html
    assert '<meta property="og:description"' in html
    assert (
        '<meta property="og:image" content="https://stellody.com'
        '/static/stellody-options-2.png"'
    ) in html
    assert '<meta name="twitter:card" content="summary_large_image"' in html
    assert '<meta name="twitter:site" content="@stellody"' in html


def test_homepage_has_keyword_rich_title_and_meta_description(
    client: TestClient,
) -> None:
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Jinja auto-escapes the ampersand in HTML output.
    assert (
        "<title>Stellody | Spotify Playlist Generator for Local and Streaming Music"
        "</title>"
    ) in html
    assert (
        '<meta name="description" content="Generate genre-sorted Spotify and local '
        "music playlists effortlessly. Stellody works with Spotify Free and Premium "
        "and local music files."
        '"'
    ) in html


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

    # Ensures sitemap de-dupe logic and cart/checkout exclusion branches are exercised.
    assert "https://stellody.com/checkout" not in xml

    assert "https://stellody.com/" in xml
    assert "https://stellody.com/pricing" in xml
    assert "https://stellody.com/contact" in xml
    assert "https://stellody.com/cart" not in xml
    assert "https://stellody.com/checkout" not in xml


def test_seo_helpers_cover_relative_and_non_relative_paths(client: TestClient) -> None:
    # Direct function coverage for branches that aren't hit via normal routing.
    from fastapi_stellody.seo import (
        DEFAULT_SEO_CONFIG,
        absolute_url,
        build_seo_context,
        canonical_url,
        robots_directive_for_path,
    )

    assert robots_directive_for_path("/pricing") is None
    assert robots_directive_for_path("/cart") == "noindex,nofollow"
    assert (
        absolute_url("pricing", config=DEFAULT_SEO_CONFIG)
        == "https://stellody.com/pricing"
    )

    class _Url:
        path = "pricing"

    class _Req:
        url = _Url()

    # Cover canonical_url() branch that normal Starlette requests don't hit
    # (request.url.path normally always starts with "/").
    assert (
        canonical_url(request=_Req(), config=DEFAULT_SEO_CONFIG)
        == "https://stellody.com/pricing"
    )

    response = client.get("/pricing")
    ctx = build_seo_context(
        request=response.request, title="Pricing", config=DEFAULT_SEO_CONFIG
    )
    assert ctx["canonical_url"] == "https://stellody.com/pricing"
    assert (
        canonical_url(request=response.request, config=DEFAULT_SEO_CONFIG)
        == "https://stellody.com/pricing"
    )


def test_sitemap_xml_covers_dedupe_and_exclusion_branches(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The sitemap handler has internal de-dupe + exclusion branches.
    # Patch PAGES to force a duplicate and a transactional page.
    from fastapi_stellody.routers import pages as pages_module

    Page = pages_module.Page
    monkeypatch.setattr(
        pages_module,
        "PAGES",
        (
            Page("/pricing", "pricing.html", "Pricing"),
            Page("/pricing", "pricing.html", "Pricing"),
            Page("/cart", "cart.html", "Cart"),
        ),
    )

    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    xml = response.text

    assert xml.count("https://stellody.com/pricing") == 1
    assert "https://stellody.com/cart" not in xml
