"""Generate application icon for Meeting Translator."""

from PIL import Image, ImageDraw, ImageFont
import os


def create_icon(output_path: str = "assets/icon.ico", size: int = 256) -> None:
    """
    Create a professional application icon.

    Args:
        output_path: Path to save the icon
        size: Icon size in pixels
    """
    # Create assets directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create a new RGBA image with gradient background
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw gradient background (dark blue to indigo)
    for y in range(size):
        # Gradient from #1a1a3e to #6366f1
        r = int(26 + (99 - 26) * (y / size))
        g = int(26 + (102 - 26) * (y / size))
        b = int(62 + (241 - 62) * (y / size))
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Draw outer circle border
    border_width = int(size * 0.05)
    draw.ellipse(
        [border_width, border_width, size - border_width, size - border_width],
        outline=(255, 255, 255, 200),
        width=border_width // 2
    )

    # Draw inner circle
    inner_margin = int(size * 0.15)
    draw.ellipse(
        [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
        fill=(99, 102, 241, 255)
    )

    # Draw speech bubble (conversation icon)
    bubble_x = int(size * 0.3)
    bubble_y = int(size * 0.25)
    bubble_w = int(size * 0.4)
    bubble_h = int(size * 0.35)

    # Main bubble
    draw.rounded_rectangle(
        [bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h],
        radius=int(size * 0.03),
        fill=(255, 255, 255, 255),
        outline=(255, 255, 255, 255),
        width=2
    )

    # Bubble tail
    tail_x = bubble_x + int(bubble_w * 0.2)
    tail_y = bubble_y + bubble_h
    draw.polygon(
        [
            (tail_x, tail_y),
            (tail_x - int(size * 0.04), tail_y + int(size * 0.06)),
            (tail_x + int(size * 0.04), tail_y + int(size * 0.05))
        ],
        fill=(255, 255, 255, 255)
    )

    # Draw globe icon inside bubble
    globe_center_x = bubble_x + bubble_w // 2
    globe_center_y = bubble_y + bubble_h // 2 - int(size * 0.03)
    globe_radius = int(size * 0.08)

    # Globe circle
    draw.ellipse(
        [
            globe_center_x - globe_radius,
            globe_center_y - globe_radius,
            globe_center_x + globe_radius,
            globe_center_y + globe_radius
        ],
        outline=(99, 102, 241, 255),
        width=2
    )

    # Meridian lines
    draw.line(
        [globe_center_x - globe_radius, globe_center_y, globe_center_x + globe_radius, globe_center_y],
        fill=(99, 102, 241, 150),
        width=1
    )
    draw.line(
        [globe_center_x, globe_center_y - globe_radius, globe_center_x, globe_center_y + globe_radius],
        fill=(99, 102, 241, 150),
        width=1
    )

    # Save as PNG first for quality
    png_path = output_path.replace(".ico", ".png")
    image.save(png_path, "PNG")
    print(f"✅ Icon PNG created: {png_path}")

    # Convert to ICO (Windows requires specific sizes)
    # Create multiple sizes for better quality at different resolutions
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon_images = []

    for w, h in sizes:
        resized = image.resize((w, h), Image.Resampling.LANCZOS)
        icon_images.append(resized)

    # Save as ICO
    icon_images[0].save(
        output_path,
        "ICO",
        sizes=[(w, h) for w, h in sizes]
    )
    print(f"✅ Icon ICO created: {output_path}")

    # Also create ICNS for macOS
    icns_path = output_path.replace(".ico", ".icns")
    try:
        # ICNS requires specific sizes
        mac_sizes = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]
        mac_images = []

        for w, h in mac_sizes:
            resized = image.resize((w, h), Image.Resampling.LANCZOS)
            mac_images.append(resized)

        mac_images[0].save(icns_path, "ICNS", sizes=[
            (16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512)
        ])
        print(f"✅ Icon ICNS created: {icns_path}")
    except Exception as e:
        print(f"⚠️  ICNS creation skipped (macOS only): {e}")


if __name__ == "__main__":
    create_icon()
