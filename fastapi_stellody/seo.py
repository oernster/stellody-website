from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


@dataclass(frozen=True)
class SeoConfig:
    canonical_host: str
    default_description: str
    default_og_image_path: str
    twitter_site: str
    twitter_card: str = "summary_large_image"


DEFAULT_SEO_CONFIG = SeoConfig(
    canonical_host="https://stellody.com",
    # Used as the homepage meta description and as a safe fallback for unknown pages.
    default_description=(
        "Stellody - Generate genre-sorted Spotify and local music "
        "playlists effortlessly."
    ),
    default_og_image_path="/static/stellody-options-2.png",
    twitter_site="@stellody",
)


def canonical_url(*, request: Request, config: SeoConfig = DEFAULT_SEO_CONFIG) -> str:
    # Canonical URLs should not include querystring/fragment.
    path = request.url.path
    if not path.startswith("/"):
        path = "/" + path
    return f"{config.canonical_host}{path}"


def robots_directive_for_path(path: str) -> str | None:
    # Avoid indexing cart/checkout to prevent thin/duplicate content.
    if path in {"/cart", "/checkout"}:
        return "noindex,nofollow"
    return None


def description_for_path(path: str, *, config: SeoConfig = DEFAULT_SEO_CONFIG) -> str:
    per_page: dict[str, str] = {
        "/pricing": (
            "Compare Stellody Standard and Pro licenses and choose the right option "
            "for your music."
        ),
        "/standard-license": (
            "Stellody Standard License: simple, affordable music licensing for your "
            "projects."
        ),
        "/pro-license": (
            "Stellody Pro License: expanded rights for professional music usage."
        ),
        "/demo": (
            "Try a Stellody demo license and see how the purchase flow works "
            "end-to-end."
        ),
        "/why-stellody": (
            "Learn what makes Stellody different and how it helps you license music "
            "faster."
        ),
        "/faq": "Answers to common questions about Stellody music licensing.",
        "/help": "Get help using Stellody and troubleshooting common issues.",
        "/change-log": "See what's new in Stellody.",
        "/contact": "Contact the Stellody team.",
        "/": config.default_description,
    }
    return per_page.get(path, config.default_description)


def absolute_url(path: str, *, config: SeoConfig = DEFAULT_SEO_CONFIG) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return f"{config.canonical_host}{path}"


def build_seo_context(
    *,
    request: Request,
    title: str,
    config: SeoConfig = DEFAULT_SEO_CONFIG,
    meta_description: str | None = None,
    meta_robots: str | None = None,
    og_title: str | None = None,
    og_description: str | None = None,
    og_image_path: str | None = None,
) -> dict[str, object]:
    canon = canonical_url(request=request, config=config)
    path = request.url.path

    resolved_description = (
        meta_description
        if meta_description is not None
        else description_for_path(path, config=config)
    )

    resolved_robots = (
        meta_robots if meta_robots is not None else robots_directive_for_path(path)
    )

    resolved_og_title = og_title if og_title is not None else f"{title} | Stellody"
    resolved_og_description = (
        og_description if og_description is not None else resolved_description
    )
    resolved_og_image = absolute_url(
        og_image_path if og_image_path is not None else config.default_og_image_path,
        config=config,
    )

    return {
        "canonical_url": canon,
        "meta_description": resolved_description,
        "meta_robots": resolved_robots,
        "og_url": canon,
        "og_title": resolved_og_title,
        "og_description": resolved_og_description,
        "og_image": resolved_og_image,
        "twitter_card": config.twitter_card,
        "twitter_site": config.twitter_site,
        "twitter_title": resolved_og_title,
        "twitter_description": resolved_og_description,
        "twitter_image": resolved_og_image,
    }
