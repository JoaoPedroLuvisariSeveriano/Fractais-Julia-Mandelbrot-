# API — PRJ.3 Fractais

## Base
`http://127.0.0.1:8000`

## `GET /health`
Retorna `{ "status": "ok" }`.

## `GET /palettes`
Retorna `{ "palettes": [...] }`.

## `POST /fractal`
Retorna PNG (`image/png`) ou SVG (`image/svg+xml`) no corpo da resposta.

### Request
```json
{
  "type": "julia" | "mandelbrot",
  "step": 0.002,
  "width": 800,
  "height": 600,
  "max_iter": 500,
  "palette": "viridis" | ["#RRGGBB", ...],
  "mode": "iteration" | "magnitude" | "smoothed", 
  "format": "png" | "svg",
  "real": <number>,
  "imag": <number>,
  "escape_radius": 2.0
}
```

### Parametrização
- Julia: `real` e `imag` formam `c = real + imag*i`.
- Mandelbrot: `real` e `imag` são um ponto central de referência.

### Erros (HTTP 400)
```json
{ "error": "...", "code": 400 }
```

