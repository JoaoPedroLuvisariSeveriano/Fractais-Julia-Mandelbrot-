from __future__ import annotations

import argparse

import requests


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app generate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate")
    gen.add_argument("--type", required=True, choices=["julia", "mandelbrot"])
    gen.add_argument("--real", type=float, required=False, default=0.0)
    gen.add_argument("--imag", type=float, required=False, default=0.0)
    gen.add_argument("--step", type=float, required=True)
    gen.add_argument("--width", type=int, default=800)
    gen.add_argument("--height", type=int, default=600)
    gen.add_argument("--max_iter", type=int, default=500)
    gen.add_argument("--escape_radius", type=float, default=2.0)
    gen.add_argument("--palette", type=str, default="viridis")
    gen.add_argument("--mode", type=str, default="smoothed", choices=["iteration", "magnitude", "smoothed"])
    gen.add_argument("--out", required=True)
    gen.add_argument("--format", type=str, default="png", choices=["png", "svg"])
    gen.add_argument("--offline", action="store_true", help="Generate locally without calling the API")
    gen.add_argument("--host", type=str, default="http://127.0.0.1:8000")

    args = parser.parse_args()

    if args.cmd == "generate":
        if args.offline:
            from .core import export_svg, generate_fractal_data
            from PIL import Image
            import io

            rgb = generate_fractal_data(
                type_=args.type,
                width=args.width,
                height=args.height,
                step=args.step,
                real=args.real,
                imag=args.imag,
                max_iter=args.max_iter,
                escape_radius=args.escape_radius,
                coloring_mode=args.mode,
                palette=args.palette
            )

            if args.format == "png":
                img = Image.fromarray(rgb, mode="RGB")
                img.save(args.out, format="PNG")
            else:
                svg = export_svg(rgb)
                with open(args.out, "w", encoding="utf-8") as f:
                    f.write(svg)
            print(f"Fractal generated offline and saved to {args.out}")

        else:
            payload = {
                "type": args.type,
                "real": args.real,
                "imag": args.imag,
                "step": args.step,
                "width": args.width,
                "height": args.height,
                "max_iter": args.max_iter,
                "escape_radius": args.escape_radius,
                "palette": args.palette,
                "mode": args.mode,
                "format": args.format,
            }

            r = requests.post(args.host + "/fractal", json=payload, timeout=60)
            if r.status_code != 200:
                raise SystemExit(f"Error {r.status_code}: {r.text}")

            with open(args.out, "wb") as f:
                f.write(r.content)
            print(f"Fractal generated via API and saved to {args.out}")


if __name__ == "__main__":
    main()

