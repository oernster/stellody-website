from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from fastapi_stellody.dependencies import get_renderer
from fastapi_stellody.rendering import PageRenderer

router = APIRouter()


@dataclass(frozen=True)
class Page:
    path: str
    template: str
    title: str


PAGES = (
    Page("/why-stellody", "why_stellody.html", "Why Stellody?"),
    Page("/pricing", "pricing.html", "Pricing"),
    Page("/pro-license", "pro_license.html", "Professional License"),
    Page("/standard-license", "standard_license.html", "Standard License"),
    Page("/upgrade-to-pro", "upgrade_to_pro.html", "Upgrade to Pro"),
    Page("/help", "help.html", "Help!"),
    Page("/faq", "faq.html", "FAQ"),
    Page("/change-log", "change_log.html", "Change-log"),
    Page("/demo", "demo.html", "Demo License"),
)


def _add_page_routes() -> None:
    for page in PAGES:

        @router.get(page.path, response_class=HTMLResponse)  # type: ignore[misc]
        async def _page(
            request: Request,
            renderer: PageRenderer = Depends(get_renderer),
            _page: Page = page,
        ):
            return renderer.render_page(
                template_name=_page.template,
                request=request,
                title=_page.title,
            )


_add_page_routes()
