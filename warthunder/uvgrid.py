import argparse
import colorsys
import string

from PIL import Image, ImageDraw, ImageFont


def font(size):
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def main():
    p = argparse.ArgumentParser(description="Write a numbered, colored UV test grid as a skin color texture.")
    p.add_argument("out", help="output file, .tga or .png")
    p.add_argument("--size", type=int, default=4096)
    p.add_argument("--cells", type=int, default=16)
    a = p.parse_args()
    cell = a.size / a.cells
    img = Image.new("RGB", (a.size, a.size))
    d = ImageDraw.Draw(img)
    big = font(int(cell * 0.32))
    for row in range(a.cells):
        for col in range(a.cells):
            hue = col / a.cells
            light = 0.35 + 0.4 * (row % 2) + 0.1 * ((row // 2) % 2)
            rgb = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue, light, 0.75))
            x0, y0 = col * cell, row * cell
            d.rectangle([x0, y0, x0 + cell, y0 + cell], fill=rgb)
            sub = cell / 4
            for i in range(1, 4):
                d.line([x0 + i * sub, y0, x0 + i * sub, y0 + cell], fill=(0, 0, 0), width=2)
                d.line([x0, y0 + i * sub, x0 + cell, y0 + i * sub], fill=(0, 0, 0), width=2)
            d.rectangle([x0, y0, x0 + cell, y0 + cell], outline=(0, 0, 0), width=6)
            label = f"{string.ascii_uppercase[col % 26]}{row + 1}"
            ink = (0, 0, 0) if light > 0.5 else (255, 255, 255)
            d.text((x0 + cell / 2, y0 + cell / 2), label, fill=ink, font=big, anchor="mm")
            d.text((x0 + cell * 0.1, y0 + cell * 0.08), "F", fill=ink, font=font(int(cell * 0.14)))
    img.save(a.out)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
