from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
ICON_PATH = ASSETS_DIR / "tiktok_fps_bypasser.ico"
PNG_PATH = ASSETS_DIR / "tiktok_fps_bypasser.png"


def make_gradient(width, height, top, bottom):
    image = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        red = int(top[0] + (bottom[0] - top[0]) * ratio)
        green = int(top[1] + (bottom[1] - top[1]) * ratio)
        blue = int(top[2] + (bottom[2] - top[2]) * ratio)
        draw.line((0, y, width, y), fill=(red, green, blue, 255))
    return image


def main():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    size = 256
    image = make_gradient(size, size, (16, 35, 63), (7, 11, 18))
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse((120, -10, 280, 150), fill=(29, 78, 216, 110))
    overlay_draw.ellipse((-30, 120, 140, 280), fill=(249, 115, 22, 125))
    overlay = overlay.filter(ImageFilter.GaussianBlur(18))
    image = Image.alpha_composite(image, overlay)

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((28, 28, 228, 228), radius=44, outline=(214, 229, 246, 185), width=4, fill=(14, 23, 38, 196))
    draw.rounded_rectangle((48, 48, 208, 208), radius=32, fill=(17, 28, 45, 230))

    try:
        big_font = ImageFont.truetype("arialbd.ttf", 78)
        small_font = ImageFont.truetype("arialbd.ttf", 26)
    except Exception:
        big_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text((67, 68), "FPS", fill=(244, 244, 245, 255), font=small_font)
    draw.text((64, 104), "60", fill=(249, 115, 22, 255), font=big_font)
    draw.text((148, 120), "->", fill=(215, 229, 246, 255), font=big_font)
    draw.text((168, 104), "30", fill=(96, 165, 250, 255), font=big_font)

    image.save(PNG_PATH)
    image.save(ICON_PATH, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])


if __name__ == "__main__":
    main()
