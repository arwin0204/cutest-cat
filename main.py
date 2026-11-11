#!/usr/bin/env python3
"""Draw the cutest cat (make.fun bounty cutest-cat-01).

Writes one 640x640 PNG of an orange tabby cat face to argv[1]
(default /output/entry.png). Python 3.13 standard library only,
no network, fully deterministic: two runs write identical bytes.
"""

import math
import struct
import sys
import zlib

W = 640
H = 640

# palette
PEACH = (255, 228, 196)
DOT = (255, 205, 165)
ORANGE = (245, 166, 64)
DARK_ORANGE = (214, 128, 32)
CREAM = (255, 236, 210)
INNER_EAR = (255, 170, 190)
PINK = (235, 110, 130)
GREEN = (70, 160, 90)
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
BLUSH = (255, 170, 175)
WHISKER = (110, 85, 70)
RED = (220, 60, 70)
DARK_RED = (190, 40, 55)


def set_px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = color[0]
        buf[i + 1] = color[1]
        buf[i + 2] = color[2]


def fill_circle(buf, cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                set_px(buf, x, y, color)


def fill_ellipse(buf, cx, cy, rx, ry, color):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                set_px(buf, x, y, color)


def fill_triangle(buf, p1, p2, p3, color):
    def sign(a, b, c):
        return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])

    d = sign(p1, p2, p3)
    if d == 0:
        return
    minx = min(p1[0], p2[0], p3[0])
    maxx = max(p1[0], p2[0], p3[0])
    miny = min(p1[1], p2[1], p3[1])
    maxy = max(p1[1], p2[1], p3[1])
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            s1 = sign((x, y), p1, p2)
            s2 = sign((x, y), p2, p3)
            s3 = sign((x, y), p3, p1)
            if (d > 0 and s1 >= 0 and s2 >= 0 and s3 >= 0) or (
                d < 0 and s1 <= 0 and s2 <= 0 and s3 <= 0
            ):
                set_px(buf, x, y, color)


def line(buf, x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(buf, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def thick_line(buf, x0, y0, x1, y1, w, color):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        fill_circle(buf, x, y, w // 2, color)


def thick_arc(buf, cx, cy, r, a0, a1, w, color):
    steps = max(int(abs(a1 - a0) * r), 1)
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        x = round(cx + r * math.cos(a))
        y = round(cy + r * math.sin(a))
        fill_circle(buf, x, y, w // 2, color)


def draw_cat(buf):
    # background
    for i in range(0, W * H * 3, 3):
        buf[i] = PEACH[0]
        buf[i + 1] = PEACH[1]
        buf[i + 2] = PEACH[2]
    # polka dots
    for row, gy in enumerate(range(40, H, 80)):
        off = 40 if row % 2 else 0
        for gx in range(40 + off, W, 80):
            fill_circle(buf, gx, gy, 13, DOT)
    # ears (behind head)
    fill_triangle(buf, (175, 215), (225, 105), (290, 200), ORANGE)
    fill_triangle(buf, (465, 215), (415, 105), (350, 200), ORANGE)
    # inner ears
    fill_triangle(buf, (200, 195), (228, 130), (268, 190), INNER_EAR)
    fill_triangle(buf, (440, 195), (412, 130), (372, 190), INNER_EAR)
    # head
    fill_circle(buf, 320, 350, 185, ORANGE)
    # forehead stripes
    thick_line(buf, 285, 185, 275, 235, 14, DARK_ORANGE)
    thick_line(buf, 320, 175, 320, 230, 14, DARK_ORANGE)
    thick_line(buf, 355, 185, 365, 235, 14, DARK_ORANGE)
    # cheek stripes
    thick_line(buf, 170, 380, 200, 370, 10, DARK_ORANGE)
    thick_line(buf, 175, 410, 205, 405, 10, DARK_ORANGE)
    thick_line(buf, 470, 380, 440, 370, 10, DARK_ORANGE)
    thick_line(buf, 465, 410, 435, 405, 10, DARK_ORANGE)
    # eyes (bigger iris, smaller pupil: softer gaze)
    for cx in (250, 390):
        fill_circle(buf, cx, 330, 45, GREEN)
        fill_circle(buf, cx, 330, 15, BLACK)
        fill_circle(buf, cx - 15, 330 - 15, 12, WHITE)
    # muzzle
    fill_ellipse(buf, 320, 430, 95, 60, CREAM)
    # nose
    fill_triangle(buf, (295, 400), (345, 400), (320, 428), PINK)
    # mouth: small w shape
    thick_line(buf, 320, 428, 320, 448, 5, BLACK)
    thick_arc(buf, 302, 448, 18, 0.0, math.pi, 5, BLACK)
    thick_arc(buf, 338, 448, 18, 0.0, math.pi, 5, BLACK)
    # blush (a touch bigger for a friendlier face)
    fill_circle(buf, 218, 425, 25, BLUSH)
    fill_circle(buf, 422, 425, 25, BLUSH)
    # whiskers
    for y0, y1 in ((415, 395), (435, 435), (455, 475)):
        thick_line(buf, 245, y0, 150, y1, 3, WHISKER)
        thick_line(buf, 395, y0, 490, y1, 3, WHISKER)
    # red bow on the right ear
    fill_triangle(buf, (395, 132), (420, 150), (395, 168), RED)
    fill_triangle(buf, (445, 132), (420, 150), (445, 168), RED)
    fill_circle(buf, 420, 150, 10, DARK_RED)


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(buf):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", comp)
        + chunk(b"IEND", b"")
    )


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    buf = bytearray(W * H * 3)
    draw_cat(buf)
    png = encode_png(buf)
    with open(out, "wb") as f:
        f.write(png)
    print(f"wrote {out} ({len(png)} bytes, 640x640)")


if __name__ == "__main__":
    main()
