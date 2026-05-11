from __future__ import annotations

import numpy as np

from .utils import ValidationError, normalize_hex_color


DEFAULT_PALETTES: dict[str, list[str]] = {
    "viridis": ["#440154", "#482878", "#3E4989", "#31688E", "#26828E", "#FDE725"],
    "plasma": ["#0D0887", "#6A00A8", "#B12A90", "#E16462", "#FCA636", "#F0F921"],
    "magma": ["#000004", "#3B0F70", "#8C2981", "#DE4968", "#F89F5D", "#FCFFA4"],
    "inferno": ["#000004", "#420A68", "#932667", "#D84B5C", "#FBA65D", "#FCFFA4"],
    "cividis": ["#00224E", "#1F7A8C", "#4DAA6A", "#8FD644", "#DCE318", "#FDE725"],
    "twilight": ["#03071E", "#370617", "#6A040F", "#9D0208", "#E85D04", "#FFBA08"],
}


def hex_to_rgb01(hex_color: str) -> np.ndarray:
    hex_color = normalize_hex_color(hex_color)
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return np.array([r, g, b], dtype=np.float32) / 255.0


def build_palette_rgba(palette_colors: list[str], *, n: int = 256) -> np.ndarray:
    # Linear interpolation between provided colors.
    if len(palette_colors) < 2:
        raise ValidationError("palette must have at least 2 colors")

    cols = np.stack([hex_to_rgb01(c) for c in palette_colors], axis=0)  # (k,3)
    k = cols.shape[0]
    x = np.linspace(0.0, 1.0, k, dtype=np.float32)
    xi = np.linspace(0.0, 1.0, n, dtype=np.float32)

    out = np.zeros((n, 3), dtype=np.float32)
    for ch in range(3):
        out[:, ch] = np.interp(xi, x, cols[:, ch])

    return out


def resolve_palette(palette: str | list[str] | None) -> list[str]:
    if palette is None:
        palette = "viridis"

    if isinstance(palette, str):
        name = palette.lower().strip()
        if name not in DEFAULT_PALETTES:
            raise ValidationError(f"Unknown palette '{palette}'. Available: {sorted(DEFAULT_PALETTES)}")
        return DEFAULT_PALETTES[name]

    # list[str]
    if isinstance(palette, list):
        if len(palette) < 6:
            raise ValidationError("palette must have at least 6 colors")
        return [normalize_hex_color(c) for c in palette]

    raise ValidationError("palette must be a string name or list of hex colors")


def colorize_1d(t: np.ndarray, palette_lut: np.ndarray) -> np.ndarray:
    """t in [0,1], shape (H,W) -> RGB uint8 (H,W,3)."""
    t = np.clip(t, 0.0, 1.0)
    idx = (t * (palette_lut.shape[0] - 1)).astype(np.int32)
    rgb = (palette_lut[idx] * 255.0).astype(np.uint8)
    return rgb

