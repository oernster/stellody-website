from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Stellody Reimagined Multi-Page")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))





@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "title": "Home",
        },
    )


@app.get("/why-stellody", response_class=HTMLResponse)
async def why_stellody(request: Request):
    return templates.TemplateResponse(
        "why_stellody.html",
        {
            "request": request,
            "title": "Why Stellody?",
        },
    )


@app.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    return templates.TemplateResponse(
        "pricing.html",
        {
            "request": request,
            "title": "Pricing",
        },
    )


@app.get("/pro-license", response_class=HTMLResponse)
async def pro_license(request: Request):
    return templates.TemplateResponse(
        "pro_license.html",
        {
            "request": request,
            "title": "Professional License",
        },
    )


@app.get("/standard-license", response_class=HTMLResponse)
async def standard_license(request: Request):
    return templates.TemplateResponse(
        "standard_license.html",
        {
            "request": request,
            "title": "Standard License",
        },
    )


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    return templates.TemplateResponse(
        "help.html",
        {
            "request": request,
            "title": "Help!",
        },
    )


@app.get("/faq", response_class=HTMLResponse)
async def faq(request: Request):
    return templates.TemplateResponse(
        "faq.html",
        {
            "request": request,
            "title": "FAQ",
        },
    )


@app.get("/change-log", response_class=HTMLResponse)
async def change_log(request: Request):
    return templates.TemplateResponse(
        "change_log.html",
        {
            "request": request,
            "title": "Change-log",
        },
    )


@app.get("/contact", response_class=HTMLResponse)
async def contact_get(request: Request):
    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "title": "Contact",
        },
    )


@app.post("/contact")
async def contact_post(
    name: str = Form(...),
    email: str = Form(...),
    msg: str = Form(...),
):
    """Placeholder form handler.

    In a real site you would send an email, persist to a DB, or create a support ticket.
    """
    _ = (name, email, msg)
    return RedirectResponse(url="/", status_code=303)


@app.get("/demo", response_class=HTMLResponse)
async def demo(request: Request):
    return templates.TemplateResponse(
        "demo.html",
        {
            "request": request,
            "title": "Demo License",
        },
    )


@app.get("/cart", response_class=HTMLResponse)
async def cart(request: Request):
    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "title": "Cart",
        },
    )


@app.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request):
    return templates.TemplateResponse(
        "checkout.html",
        {
            "request": request,
            "title": "Checkout",
        },
    )

