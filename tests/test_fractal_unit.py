from __future__ import annotations

import numpy as np

from app.fractal import mandelbrot, julia


def test_mandelbrot_small_shape_and_ranges():
    res = mandelbrot(width=40, height=30, step=0.01, x0=-2.0, y0=-1.0, max_iter=50, escape_radius=2.0)
    assert res.escape_iter.shape == (30, 40)
    assert res.smooth.shape == (30, 40)
    assert res.magnitude.shape == (30, 40)
    assert np.isfinite(res.escape_iter).all()


def test_julia_small_shape_and_ranges():
    res = julia(width=32, height=24, step=0.01, c_real=-0.7, c_imag=0.27015, max_iter=50, escape_radius=2.0)
    assert res.escape_iter.shape == (24, 32)
    assert np.isfinite(res.smooth).all()

