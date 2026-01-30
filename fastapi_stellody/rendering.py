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
        # Jinja2Templates has TemplateResponse(template, context)
        return self.templates.TemplateResponse(
            template_name,
            {
                "request": request,
                "title": title,
            },
        )
