from __future__ import annotations

import io
from typing import Any

import numpy as np
from PIL import Image

from .color import build_palette_rgba, resolve_palette
from .fractal import julia as julia_fn, mandelbrot as mandelbrot_fn
from .utils import ValidationError


def generate_fractal_data(
    type_: str,
    width: int,
    height: int,
    step: float,
    *,
    real: float = 0.0,
    imag: float = 0.0,
    max_iter: int = 500,
    escape_radius: float = 2.0,
    coloring_mode: str = "smoothed",
    palette: str | list[str] = "viridis",
) -> np.ndarray:
    """Generates the fractal and returns an RGB uint8 numpy array (H, W, 3)."""
    
    if type_ == "julia":
        # Compute x0,y0 so that (0,0) is at the center of the image
        x0 = 0.0 - (width // 2) * step
        y0 = 0.0 - (height // 2) * step
        result = julia_fn(width, height, step, c_real=real, c_imag=imag, x0=x0, y0=y0, max_iter=max_iter, escape_radius=escape_radius)
    elif type_ == "mandelbrot":
        # Compute x0,y0 so that center is at middle pixel
        x0 = real - (width // 2) * step
        y0 = imag - (height // 2) * step
        result = mandelbrot_fn(width, height, step, x0=x0, y0=y0, max_iter=max_iter, escape_radius=escape_radius)
    else:
        raise ValidationError(f"Invalid fractal type: {type_}")

    # Determine scalar field to map to colors.
    if coloring_mode == "iteration":
        t = result.escape_iter / float(max_iter)
    elif coloring_mode == "magnitude":
        t = np.log1p(result.magnitude) / np.log1p(float(escape_radius) + float(max_iter))
    else:
        t = result.smooth / float(max_iter)

    palette_colors = resolve_palette(palette)
    lut = build_palette_rgba(palette_colors, n=256)

    # Map t to RGB
    indices = (np.clip(t, 0.0, 1.0) * (lut.shape[0] - 1)).astype(np.int32)
    rgb = (lut[indices] * 255.0).astype(np.uint8)
    
    return rgb


def export_svg(rgb: np.ndarray, max_cells: int = 120000) -> str:
    height, width, _ = rgb.shape
    scale = int(np.ceil((width * height) / max_cells))
    scale = max(scale, 1)
    w2 = width // scale
    h2 = height // scale

    img_small = Image.fromarray(rgb, mode="RGB").resize((w2, h2), resample=Image.BOX)
    arr = np.array(img_small)

    rects = []
    for y in range(h2):
        for x in range(w2):
            r, g, b = arr[y, x]
            rects.append(f"<rect x='{x}' y='{y}' width='1' height='1' fill='rgb({r},{g},{b})' />")

    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' "
        f"width='{w2}' height='{h2}' viewBox='0 0 {w2} {h2}'>" + "".join(rects) + "</svg>"
    )
    return svg
