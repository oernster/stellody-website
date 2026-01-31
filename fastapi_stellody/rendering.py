from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import Request
from starlette.responses import Response


class PageRenderer(Protocol):
    def render_page(
        self, *, template_name: str, request: Request, title: str
    ) -> Response:
        """Render an HTML page."""


@dataclass(frozen=True)
class JinjaPageRenderer:
    templates: object

    def render_page(
        self, *, template_name: str, request: Request, title: str
    ) -> Response:
        # Starlette >=0.36 expects TemplateResponse(request, name, context)
        # (older TemplateResponse(name, context) is deprecated).
        return self.templates.TemplateResponse(
            request,
            template_name,
            {
                "title": title,
                # Make query params available in templates (e.g. ?sent=1 / ?error=1).
                "request": request,
            },
        )
