#!/usr/bin/env python3
"""
Generate placeholder desktop icons for the Ottoman Agent desktop app.

Pure-stdlib implementation (no Pillow required):
- desktop/resources/icon.png  (256x256, used by the Electron window)
- desktop/resources/icon.ico  (256x256 PNG-compressed ICO entry)
- desktop/resources/icon.icns (ic08/ic09/ic13 PNG entries for macOS)

Design: dark navy background with a golden crescent-and-star motif.
Run: python scripts/generate_icons.py
"""

import struct
import zlib
from pathlib import Path

RESOURCES = Path(__file__).resolve().parent.parent / "desktop" / "resources"

# Palette
BG = (26, 26, 46)  # #1a1a2e dark navy
GOLD = (212, 168, 83)  # #d4a853
GOLD_LIGHT = (238, 205, 130)
STAR = (245, 226, 176)


def make_pixels(size: int) -> bytes:
    """Generate RGBA pixel data for the icon at the given size."""
    rows = bytearray()
    cx = cy = size / 2.0
    radius = size * 0.34
    star_r = size * 0.075
    star_x, star_y = cx + size * 0.14, cy - size * 0.12

    def dist(px, py, ox, oy):
        return ((px - ox) ** 2 + (py - oy) ** 2) ** 0.5

    for y in range(size):
        row = bytearray()
        for x in range(size):
            # Crescent: big circle minus offset circle
            d_outer = dist(x + 0.5, y + 0.5, cx, cy)
            d_inner = dist(x + 0.5, y + 0.5, cx + size * 0.13, cy - size * 0.05)
            d_star = dist(x + 0.5, y + 0.5, star_x, star_y)

            if d_outer <= radius and d_inner >= radius * 0.78:
                # rim highlight
                if radius - d_outer < size * 0.03:
                    color = GOLD_LIGHT
                else:
                    color = GOLD
            elif d_star <= star_r:
                color = STAR
            else:
                color = BG
            row += bytes(color) + b"\xff"
        rows += row
    return bytes(rows)


def write_png(path: Path, size: int, pixels: bytes) -> None:
    """Write a minimal valid PNG (RGBA, no filters)."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    raw = b"".join(
        b"\x00" + pixels[y * size * 4 : (y + 1) * size * 4] for y in range(size)
    )
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def write_ico(path: Path, size: int, png_bytes: bytes) -> None:
    """Wrap a PNG into a single-entry ICO (Vista+ supports PNG entries)."""
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack(
        "<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(png_bytes), 22
    )
    path.write_bytes(header + entry + png_bytes)


def write_icns(path: Path, entries: list[tuple[bytes, bytes]]) -> None:
    """Write ICNS with PNG entries: [(type, png_bytes), ...]."""
    body = b"".join(struct.pack(">4sI", t, len(d) + 8) + d for t, d in entries)
    path.write_bytes(b"icns" + struct.pack(">I", len(body) + 8) + body)


def main() -> None:
    RESOURCES.mkdir(parents=True, exist_ok=True)

    pngs = {}
    for size in (256, 512, 1024):
        pngs[size] = make_pixels(size)

    # icon.png: 256x256 (Electron window icon)
    write_png(RESOURCES / "icon.png", 256, pngs[256])
    print("wrote", RESOURCES / "icon.png")

    # icon.ico: PNG-compressed 256x256 entry
    write_ico(RESOURCES / "icon.ico", 256, pngs[256])
    print("wrote", RESOURCES / "icon.ico")

    # icon.icns: 256 / 512 / 1024 PNG entries
    icns_pngs = {
        b"ic08": (256, pngs[256]),
        b"ic09": (512, pngs[512]),
        b"ic13": (1024, pngs[1024]),
    }
    write_icns(RESOURCES / "icon.icns", [(t, p) for t, (_, p) in icns_pngs.items()])
    print("wrote", RESOURCES / "icon.icns")

    for f in ("icon.png", "icon.ico", "icon.icns"):
        p = RESOURCES / f
        print(f"  {f}: {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
