from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ValidationError(Exception):
    message: str
    code: int = 400


def clamp_int(value: int, min_v: int, max_v: int, *, field: str) -> int:
    if not isinstance(value, int):
        raise ValidationError(f"{field} must be an integer")
    if value < min_v or value > max_v:
        raise ValidationError(f"{field} must be between {min_v} and {max_v}")
    return value


def clamp_float(value: float, min_v: float, max_v: float, *, field: str) -> float:
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{field} must be a number")
    v = float(value)
    if v < min_v or v > max_v:
        raise ValidationError(f"{field} must be between {min_v} and {max_v}")
    return v


HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def normalize_hex_color(s: str) -> str:
    if not isinstance(s, str) or not HEX_RE.match(s.strip()):
        raise ValidationError("palette hex colors must be in format #RRGGBB")
    s = s.strip()
    if not s.startswith("#"):
        s = "#" + s
    return s.upper()


def parse_palette(palette: str | list[str] | None, *, default: str = "viridis") -> list[str]:
    if palette is None:
        palette = default

    if isinstance(palette, str):
        # Name-based lookup happens in color.py; keep raw name here.
        return [palette]

    if isinstance(palette, list):
        if len(palette) < 6:
            raise ValidationError("custom palette must have at least 6 colors")
        return [normalize_hex_color(c) for c in palette]

    raise ValidationError("palette must be a string name or a list of hex colors")

