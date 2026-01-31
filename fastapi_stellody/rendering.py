from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import Request
from starlette.responses import Response

from fastapi_stellody.seo import DEFAULT_SEO_CONFIG, build_seo_context


class PageRenderer(Protocol):
    def render_page(
        self,
        *,
        template_name: str,
        request: Request,
        title: str,
        meta_description: str | None = None,
        meta_robots: str | None = None,
        og_title: str | None = None,
        og_description: str | None = None,
        og_image_path: str | None = None,
        **context: object,
    ) -> Response:
        """Render an HTML page."""


@dataclass(frozen=True)
class JinjaPageRenderer:
    templates: object

    def render_page(
        self,
        *,
        template_name: str,
        request: Request,
        title: str,
        meta_description: str | None = None,
        meta_robots: str | None = None,
        og_title: str | None = None,
        og_description: str | None = None,
        og_image_path: str | None = None,
        **context: object,
    ) -> Response:
        # Starlette >=0.36 expects TemplateResponse(request, name, context)
        # (older TemplateResponse(name, context) is deprecated).

        seo_context = build_seo_context(
            request=request,
            title=title,
            config=DEFAULT_SEO_CONFIG,
            meta_description=meta_description,
            meta_robots=meta_robots,
            og_title=og_title,
            og_description=og_description,
            og_image_path=og_image_path,
        )

        return self.templates.TemplateResponse(
            request,
            template_name,
            {
                "title": title,
                # Make query params available in templates (e.g. ?sent=1 / ?error=1).
                "request": request,
                **seo_context,
                **context,
            },
        )
