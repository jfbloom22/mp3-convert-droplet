#!/usr/bin/env python3
"""Render the app icon PNG with explicit transparent corners."""

from __future__ import annotations

import argparse
import math
import struct
import zlib
from pathlib import Path


Pixel = tuple[int, int, int, int]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=1024)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def blend(dst: Pixel, src: Pixel) -> Pixel:
    sr, sg, sb, sa = src
    if sa == 0:
        return dst
    dr, dg, db, da = dst
    alpha = sa / 255
    out_a = alpha + da / 255 * (1 - alpha)
    if out_a == 0:
        return (0, 0, 0, 0)
    return (
        round((sr * alpha + dr * da / 255 * (1 - alpha)) / out_a),
        round((sg * alpha + dg * da / 255 * (1 - alpha)) / out_a),
        round((sb * alpha + db * da / 255 * (1 - alpha)) / out_a),
        round(out_a * 255),
    )


def in_rounded_rect(x: float, y: float, size: int, radius: float) -> bool:
    left = radius
    right = size - radius
    top = radius
    bottom = size - radius
    if left <= x <= right or top <= y <= bottom:
        return True
    cx = left if x < left else right
    cy = top if y < top else bottom
    return (x - cx) ** 2 + (y - cy) ** 2 <= radius**2


def point_in_poly(x: float, y: float, points: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(points) - 1
    for i, point in enumerate(points):
        xi, yi = point
        xj, yj = points[j]
        intersects = (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi
        if intersects:
            inside = not inside
        j = i
    return inside


def draw_circle(buf: list[Pixel], size: int, cx: float, cy: float, radius: float, color: Pixel) -> None:
    min_x = max(0, math.floor(cx - radius))
    max_x = min(size - 1, math.ceil(cx + radius))
    min_y = max(0, math.floor(cy - radius))
    max_y = min(size - 1, math.ceil(cy + radius))
    radius2 = radius * radius
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= radius2:
                idx = y * size + x
                buf[idx] = blend(buf[idx], color)


def draw_rounded_rect(
    buf: list[Pixel],
    size: int,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    radius: float,
    color: Pixel,
) -> None:
    for y in range(max(0, math.floor(y0)), min(size - 1, math.ceil(y1)) + 1):
        for x in range(max(0, math.floor(x0)), min(size - 1, math.ceil(x1)) + 1):
            px = x + 0.5
            py = y + 0.5
            cx = min(max(px, x0 + radius), x1 - radius)
            cy = min(max(py, y0 + radius), y1 - radius)
            if (px - cx) ** 2 + (py - cy) ** 2 <= radius**2:
                idx = y * size + x
                buf[idx] = blend(buf[idx], color)


def draw_poly(buf: list[Pixel], size: int, points: list[tuple[float, float]], color: Pixel) -> None:
    min_x = max(0, math.floor(min(p[0] for p in points)))
    max_x = min(size - 1, math.ceil(max(p[0] for p in points)))
    min_y = max(0, math.floor(min(p[1] for p in points)))
    max_y = min(size - 1, math.ceil(max(p[1] for p in points)))
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if point_in_poly(x + 0.5, y + 0.5, points):
                idx = y * size + x
                buf[idx] = blend(buf[idx], color)


def write_png(path: Path, width: int, height: int, pixels: list[Pixel]) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for pixel in pixels[y * width : (y + 1) * width]:
            raw.extend(pixel)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def main() -> int:
    args = parse_args()
    size = args.size
    buf: list[Pixel] = [(0, 0, 0, 0)] * (size * size)
    radius = size * 0.215

    for y in range(size):
        for x in range(size):
            if not in_rounded_rect(x + 0.5, y + 0.5, size, radius):
                continue
            t = (x + y) / (2 * size)
            r = lerp(37, 17, t)
            g = lerp(54, 24, t)
            b = lerp(77, 39, t)
            buf[y * size + x] = (r, g, b, 255)

    s = size / 1024
    draw_circle(buf, size, 290 * s, 265 * s, 120 * s, (255, 255, 255, 18))
    draw_circle(buf, size, 770 * s, 760 * s, 170 * s, (56, 189, 248, 20))

    blue = (57, 136, 244, 255)
    light_blue = (140, 211, 250, 255)
    draw_circle(buf, size, 350 * s, 735 * s, 82 * s, blue)
    draw_rounded_rect(buf, size, 405 * s, 280 * s, 500 * s, 730 * s, 46 * s, blue)
    draw_poly(
        buf,
        size,
        [(430 * s, 280 * s), (700 * s, 230 * s), (760 * s, 300 * s), (500 * s, 350 * s)],
        light_blue,
    )
    draw_rounded_rect(buf, size, 645 * s, 245 * s, 760 * s, 570 * s, 46 * s, blue)

    orange = (249, 115, 22, 255)
    yellow = (251, 191, 36, 255)
    draw_rounded_rect(buf, size, 525 * s, 505 * s, 710 * s, 675 * s, 34 * s, yellow)
    draw_poly(
        buf,
        size,
        [(675 * s, 450 * s), (850 * s, 590 * s), (675 * s, 735 * s)],
        orange,
    )
    draw_rounded_rect(buf, size, 525 * s, 590 * s, 710 * s, 675 * s, 28 * s, orange)

    for i in range(14):
        y = (800 + i) * s
        for x in range(round(190 * s), round(830 * s)):
            curve_y = (810 + 60 * math.sin((x / s - 190) / 640 * math.pi)) * s
            if abs(y - curve_y) < 7 * s:
                idx = round(y) * size + x
                if 0 <= idx < len(buf):
                    buf[idx] = blend(buf[idx], (255, 255, 255, 30))

    write_png(args.out, size, size, buf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
