from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient


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


def test_contact_post_redirects_to_home(client: TestClient) -> None:
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
    assert response.headers["location"] == "/"

    # Exercise the handler body for full coverage.
    response = client.post(
        "/contact",
        data={
            "name": "Coverage User",
            "email": "coverage@example.com",
            "msg": "Coverage",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    _assert_html_title(response.text, "Home")


def test_static_assets_are_served(client: TestClient) -> None:
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    # Keep assertion minimal and resilient.
    assert "text/css" in response.headers.get("content-type", "")
