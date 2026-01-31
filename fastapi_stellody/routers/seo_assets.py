from __future__ import annotations

from fastapi import APIRouter
from starlette.responses import PlainTextResponse, Response

from fastapi_stellody.routers import pages
from fastapi_stellody.seo import DEFAULT_SEO_CONFIG, absolute_url

router = APIRouter()


@router.get("/robots.txt", include_in_schema=False)
async def robots_txt() -> PlainTextResponse:
    # Default allow-all, with targeted disallows for thin/transactional flows.
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /cart",
            "Disallow: /checkout",
            f"Sitemap: {DEFAULT_SEO_CONFIG.canonical_host}/sitemap.xml",
            "",
        ]
    )
    return PlainTextResponse(content, media_type="text/plain")


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml() -> Response:
    # Sitemap scope: /, all static pages, and /contact. Excludes /cart and /checkout.
    paths = ["/"] + [p.path for p in pages.PAGES] + ["/contact"]
    # Preserve order while de-duping.
    seen: set[str] = set()
    unique_paths: list[str] = []
    for path in paths:
        if path in seen:
            continue
        if path in {"/cart", "/checkout"}:
            continue
        seen.add(path)
        unique_paths.append(path)

    urls = "\n".join(
        f"    <url><loc>{absolute_url(path, config=DEFAULT_SEO_CONFIG)}</loc></url>"
        for path in unique_paths
    )

    xml = "\n".join(
        [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
            urls,
            "</urlset>",
            "",
        ]
    )

    return Response(content=xml, media_type="application/xml")

