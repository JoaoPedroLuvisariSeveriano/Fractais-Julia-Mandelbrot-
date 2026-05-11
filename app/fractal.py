from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numba import njit


@dataclass(frozen=True)
class FractalResult:
    escape_iter: np.ndarray  # float32 (H,W)
    smooth: np.ndarray  # float32 (H,W)
    magnitude: np.ndarray  # float32 (H,W)


def _smooth_iteration(n: np.ndarray, z_abs: np.ndarray, log_escape_radius: float) -> np.ndarray:
    # Continuous (smooth) iteration count:
    # mu = n + 1 - log2(log|z_n| / log|R|)
    # This maps z_abs in [R, R^2] to [n+1, n]
    eps = 1e-12
    z_abs = np.maximum(z_abs, eps)
    # Correct formula: mu = n + 1 - (log(log|z|) - log(log R)) / log(2)
    mu = n + 1 - (np.log(np.log(z_abs)) - np.log(log_escape_radius)) / np.log(2.0)
    return mu


def mandelbrot(width: int, height: int, step: float, *,
               x0: float = -2.5, y0: float = -1.25,
               max_iter: int = 500, escape_radius: float = 2.0,
               ) -> FractalResult:
    # Coordinates: x = x0 + px*step ; y = y0 + py*step
    xs = x0 + np.arange(width, dtype=np.float64) * step
    ys = y0 + np.arange(height, dtype=np.float64) * step
    X, Y = np.meshgrid(xs, ys)

    C_real = X
    C_imag = Y

    Z_real = np.zeros_like(C_real)
    Z_imag = np.zeros_like(C_imag)

    escape_iter = np.zeros((height, width), dtype=np.float32)
    smooth = np.zeros((height, width), dtype=np.float32)
    magnitude = np.zeros((height, width), dtype=np.float32)

    R2 = escape_radius * escape_radius
    mask = np.ones((height, width), dtype=bool)

    for n in range(max_iter):
        # z = z^2 + c
        zr2 = Z_real * Z_real
        zi2 = Z_imag * Z_imag
        Z_imag = 2.0 * Z_real * Z_imag + C_imag
        Z_real = zr2 - zi2 + C_real

        mag2 = Z_real * Z_real + Z_imag * Z_imag
        escaped = mask & (mag2 > R2)
        if np.any(escaped):
            mag = np.sqrt(mag2[escaped])
            magnitude[escaped] = mag.astype(np.float32)
            escape_iter[escaped] = float(n + 1)

            mu = _smooth_iteration(
                np.array(n + 1, dtype=np.float64),
                np.array(mag, dtype=np.float64),
                math.log(escape_radius),
            )
            smooth[escaped] = mu.astype(np.float32)

            mask[escaped] = False

        if not mask.any():
            break

    # For points that never escaped, keep smooth/escape_iter at max_iter.
    escape_iter[mask] = float(max_iter)
    smooth[mask] = float(max_iter)
    magnitude[mask] = np.sqrt(Z_real[mask] * Z_real[mask] + Z_imag[mask] * Z_imag[mask]).astype(np.float32)

    return FractalResult(escape_iter=escape_iter, smooth=smooth, magnitude=magnitude)


def julia(width: int, height: int, step: float, *,
          c_real: float, c_imag: float,
          x0: float = -1.5, y0: float = -1.5,
          max_iter: int = 500, escape_radius: float = 2.0,
          ) -> FractalResult:
    xs = x0 + np.arange(width, dtype=np.float64) * step
    ys = y0 + np.arange(height, dtype=np.float64) * step
    X, Y = np.meshgrid(xs, ys)

    Z_real = X
    Z_imag = Y

    escape_iter = np.zeros((height, width), dtype=np.float32)
    smooth = np.zeros((height, width), dtype=np.float32)
    magnitude = np.zeros((height, width), dtype=np.float32)

    C_real = float(c_real)
    C_imag = float(c_imag)

    R2 = escape_radius * escape_radius
    mask = np.ones((height, width), dtype=bool)

    for n in range(max_iter):
        zr2 = Z_real * Z_real
        zi2 = Z_imag * Z_imag
        Z_imag = 2.0 * Z_real * Z_imag + C_imag
        Z_real = zr2 - zi2 + C_real

        mag2 = Z_real * Z_real + Z_imag * Z_imag
        escaped = mask & (mag2 > R2)
        if np.any(escaped):
            mag = np.sqrt(mag2[escaped])
            magnitude[escaped] = mag.astype(np.float32)
            escape_iter[escaped] = float(n + 1)

            mu = _smooth_iteration(
                np.array(n + 1, dtype=np.float64),
                np.array(mag, dtype=np.float64),
                math.log(escape_radius),
            )
            smooth[escaped] = mu.astype(np.float32)

            mask[escaped] = False

        if not mask.any():
            break

    escape_iter[mask] = float(max_iter)
    smooth[mask] = float(max_iter)
    magnitude[mask] = np.sqrt(Z_real[mask] * Z_real[mask] + Z_imag[mask] * Z_imag[mask]).astype(np.float32)

    return FractalResult(escape_iter=escape_iter, smooth=smooth, magnitude=magnitude)

