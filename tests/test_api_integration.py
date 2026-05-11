from __future__ import annotations

import numpy as np
from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_palettes():
    r = client.get("/palettes")
    assert r.status_code == 200
    assert "palettes" in r.json()
    assert isinstance(r.json()["palettes"], list)


def test_fractal_png_julia():
    payload = {
        "type": "julia",
        "real": -0.7,
        "imag": 0.27015,
        "step": 0.002,
        "width": 120,
        "height": 80,
        "max_iter": 100,
        "palette": "viridis",
        "mode": "smoothed",
        "format": "png",
    }
    r = client.post("/fractal", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/png")
    assert len(r.content) > 100


def test_fractal_invalid_type_returns_400():
    r = client.post(
        "/fractal",
        json={"type": "foo", "step": 0.1, "width": 10, "height": 10, "max_iter": 10, "palette": "viridis"},
    )
    assert r.status_code == 400
    j = r.json()
    assert "error" in j and "code" in j

