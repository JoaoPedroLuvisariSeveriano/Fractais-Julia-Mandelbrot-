from __future__ import annotations

import io
from typing import Any


import numpy as np
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse
from PIL import Image

from .color import build_palette_rgba, resolve_palette
from .fractal import julia as julia_fn, mandelbrot as mandelbrot_fn
from .utils import ValidationError, clamp_float, clamp_int



app = FastAPI(title="Fractal Generator API")

# CORS para permitir o frontend (Vite) acessar a API.
# Ajuste de forma segura para desenvolvimento.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




def error_json(msg: str, code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=code, content={"error": msg, "code": code})


def _normalize_coloring_mode(mode: str) -> str:
    m = mode.lower().strip()
    allowed = {"iteration", "magnitude", "smoothed"}
    if m not in allowed:
        raise ValidationError(f"Invalid mode '{mode}'. Allowed: {sorted(allowed)}")
    return m


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/palettes")
def palettes() -> dict[str, Any]:
    # Retorna os nomes das paletas predefinidas (usadas no color.py)
    from .color import DEFAULT_PALETTES

    return {"palettes": sorted(DEFAULT_PALETTES.keys())}



@app.post("/fractal")
def fractal(payload: dict[str, Any]) -> Response:
    try:
        type_ = str(payload.get("type", "")).lower().strip()
        if type_ not in {"julia", "mandelbrot"}:
            raise ValidationError("type must be 'julia' or 'mandelbrot'")

        step = clamp_float(payload.get("step"), 1e-6, 10.0, field="step")
        width = clamp_int(payload.get("width"), 16, 4096, field="width")
        height = clamp_int(payload.get("height"), 16, 4096, field="height")
        max_iter = clamp_int(payload.get("max_iter"), 1, 20000, field="max_iter")
        escape_radius = clamp_float(payload.get("escape_radius", 2.0), 0.1, 1000.0, field="escape_radius")

        coloring_mode = _normalize_coloring_mode(payload.get("mode", payload.get("coloring_mode", "smoothed")))

        fmt = str(payload.get("format", "png")).lower().strip()
        if fmt not in {"png", "svg"}:
            raise ValidationError("format must be 'png' or 'svg'")

        palette_in = payload.get("palette", "viridis")

        from .core import generate_fractal_data, export_svg

        rgb = generate_fractal_data(
            type_=type_,
            width=width,
            height=height,
            step=step,
            real=payload.get("real", 0.0),
            imag=payload.get("imag", 0.0),
            max_iter=max_iter,
            escape_radius=escape_radius,
            coloring_mode=coloring_mode,
            palette=palette_in
        )

        if fmt == "png":
            img = Image.fromarray(rgb, mode="RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return Response(content=buf.getvalue(), media_type="image/png")

        # SVG export
        svg_data = export_svg(rgb)
        return Response(content=svg_data.encode("utf-8"), media_type="image/svg+xml")

    except ValidationError as e:
        # FastAPI-friendly error shape
        return error_json(e.message, code=e.code)

    except Exception as e:
        return error_json(f"Internal error: {e}", code=500)

