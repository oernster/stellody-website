from __future__ import annotations

import os

from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter()


def _release_base_url() -> str:
    # Release tag for installer assets.
    # Default is intentionally deterministic/hard-coded to match current release.
    release_tag = os.environ.get("TAG_RELEASED_VERSION", "v1.3.0")
    return (
        "https://github.com/oernster/stellody-website/releases/download/"
        f"{release_tag}"
    )


@router.get("/downloads/stellody.dmg")
def download_stellody_dmg() -> RedirectResponse:
    return RedirectResponse(
        url=f"{_release_base_url()}/stellody.dmg",
        status_code=307,
    )


@router.get("/downloads/stellody.flatpak")
def download_stellody_flatpak() -> RedirectResponse:
    return RedirectResponse(
        url=f"{_release_base_url()}/stellody.flatpak",
        status_code=307,
    )


@router.get("/downloads/stellody_installer.exe")
def download_stellody_installer_exe() -> RedirectResponse:
    return RedirectResponse(
        url=f"{_release_base_url()}/stellody_installer.exe",
        status_code=307,
    )

