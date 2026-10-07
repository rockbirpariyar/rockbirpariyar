from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageSequence
import random
import os

INPUT = "dark-souls.gif"
OUTPUT = "profile.gif"

WIDTH = 1200
HEIGHT = 675

# -------------------------------------------------------
# WINDOWS FONTS
# -------------------------------------------------------

GEORGIA = r"C:\Windows\Fonts\georgia.ttf"
GEORGIA_BOLD = r"C:\Windows\Fonts\georgiab.ttf"
CONSOLAS = r"C:\Windows\Fonts\consola.ttf"
CONSOLAS_BOLD = r"C:\Windows\Fonts\consolab.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


TITLE_FONT = font(GEORGIA, 62)
SUB_FONT = font(CONSOLAS, 16)
SMALL_FONT = font(CONSOLAS, 12)
TINY_FONT = font(CONSOLAS, 10)


# -------------------------------------------------------
# COLORS
# -------------------------------------------------------

WHITE = (228, 220, 204, 255)
MUTED = (170, 161, 145, 255)

GOLD = (190, 136, 60, 255)
DARK_GOLD = (90, 61, 25, 255)

PANEL = (5, 5, 5, 190)


# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------

def cover(img, target_w, target_h):
    """Resize/crop image like CSS object-fit: cover."""

    w, h = img.size

    scale = max(
        target_w / w,
        target_h / h
    )

    nw = int(w * scale)
    nh = int(h * scale)

    img = img.resize((nw, nh), Image.Resampling.LANCZOS)

    left = (nw - target_w) // 2
    top = (nh - target_h) // 2

    return img.crop(
        (
            left,
            top,
            left + target_w,
            top + target_h
        )
    )


def centered_text(draw, y, text, used_font, fill):
    bbox = draw.textbbox((0, 0), text, font=used_font)

    w = bbox[2] - bbox[0]

    x = (WIDTH - w) // 2

    draw.text(
        (x, y),
        text,
        font=used_font,
        fill=fill
    )


def spaced_text(draw, center_x, y, text, used_font, spacing, fill):
    widths = []

    for c in text:
        box = draw.textbbox((0, 0), c, font=used_font)
        widths.append(box[2] - box[0])

    total = sum(widths) + spacing * (len(text) - 1)

    x = center_x - total / 2

    for c, w in zip(text, widths):
        draw.text(
            (x, y),
            c,
            font=used_font,
            fill=fill
        )

        x += w + spacing


# -------------------------------------------------------
# CINEMATIC DARKENING
# -------------------------------------------------------

def add_gradient(frame):
    overlay = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 0)
    )

    px = overlay.load()

    for y in range(HEIGHT):

        position = y / HEIGHT

        if position < 0.45:
            alpha = 15

        elif position < 0.68:
            alpha = int(
                15 +
                (position - 0.45) / 0.23 * 75
            )

        else:
            alpha = int(
                90 +
                (position - 0.68) / 0.32 * 115
            )

        for x in range(WIDTH):
            px[x, y] = (0, 0, 0, alpha)

    return Image.alpha_composite(frame, overlay)


# -------------------------------------------------------
# VIGNETTE
# -------------------------------------------------------

def add_vignette(frame):
    mask = Image.new("L", (WIDTH, HEIGHT), 0)

    draw = ImageDraw.Draw(mask)

    draw.ellipse(
        (
            -180,
            -130,
            WIDTH + 180,
            HEIGHT + 180
        ),
        fill=255
    )

    mask = mask.filter(
        ImageFilter.GaussianBlur(150)
    )

    inverted = Image.eval(
        mask,
        lambda p: 255 - p
    )

    darkness = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 220)
    )

    frame.paste(
        darkness,
        (0, 0),
        inverted
    )

    return frame


# -------------------------------------------------------
# TEXTURE / GRAIN
# -------------------------------------------------------

def add_grain(frame):
    grain = Image.new(
        "RGBA",
        frame.size,
        (0, 0, 0, 0)
    )

    pixels = grain.load()

    # Sparse grain rather than modifying every pixel.
    for _ in range(17000):

        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)

        brightness = random.randint(90, 190)
        alpha = random.randint(4, 15)

        pixels[x, y] = (
            brightness,
            brightness,
            brightness,
            alpha
        )

    return Image.alpha_composite(
        frame,
        grain
    )


# -------------------------------------------------------
# GOLD DIVIDERS
# -------------------------------------------------------

def divider(draw, y, length=270):

    cx = WIDTH // 2

    draw.line(
        (
            cx - length,
            y,
            cx - 12,
            y
        ),
        fill=DARK_GOLD,
        width=1
    )

    draw.line(
        (
            cx + 12,
            y,
            cx + length,
            y
        ),
        fill=DARK_GOLD,
        width=1
    )

    diamond = [
        (cx, y - 5),
        (cx + 5, y),
        (cx, y + 5),
        (cx - 5, y)
    ]

    draw.polygon(
        diamond,
        outline=GOLD
    )

    draw.ellipse(
        (
            cx - 1,
            y - 1,
            cx + 1,
            y + 1
        ),
        fill=(245, 200, 117, 255)
    )


# -------------------------------------------------------
# SOCIAL ICON PANELS
# -------------------------------------------------------

def social_panel(draw, x, y, icon, label):

    box = (
        x - 28,
        y - 25,
        x + 28,
        y + 25
    )

    draw.rounded_rectangle(
        box,
        radius=4,
        fill=PANEL,
        outline=(90, 66, 34, 180),
        width=1
    )

    bbox = draw.textbbox(
        (0, 0),
        icon,
        font=font(CONSOLAS_BOLD, 22)
    )

    tw = bbox[2] - bbox[0]

    draw.text(
        (
            x - tw / 2,
            y - 13
        ),
        icon,
        font=font(CONSOLAS_BOLD, 22),
        fill=WHITE
    )

    bbox = draw.textbbox(
        (0, 0),
        label,
        font=TINY_FONT
    )

    tw = bbox[2] - bbox[0]

    draw.text(
        (
            x - tw / 2,
            y + 36
        ),
        label,
        font=TINY_FONT,
        fill=MUTED
    )


# -------------------------------------------------------
# MAIN UI
# -------------------------------------------------------

def ui(frame):

    overlay = Image.new(
        "RGBA",
        frame.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(overlay)

    # Large subtle center shadow behind typography.

    center_shadow = Image.new(
        "RGBA",
        frame.size,
        (0, 0, 0, 0)
    )

    shadow_draw = ImageDraw.Draw(center_shadow)

    shadow_draw.ellipse(
        (
            270,
            330,
            930,
            740
        ),
        fill=(0, 0, 0, 155)
    )

    center_shadow = center_shadow.filter(
        ImageFilter.GaussianBlur(100)
    )

    frame = Image.alpha_composite(
        frame,
        center_shadow
    )

    overlay = Image.new(
        "RGBA",
        frame.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(overlay)


    # -----------------------------------------
    # ROCKBIR
    # -----------------------------------------

    spaced_text(
        draw,
        WIDTH // 2,
        385,
        "ROCKBIR",
        TITLE_FONT,
        9,
        WHITE
    )


    # -----------------------------------------
    # DIVIDER
    # -----------------------------------------

    divider(
        draw,
        462,
        250
    )


    # -----------------------------------------
    # SUBTITLE
    # -----------------------------------------

    spaced_text(
        draw,
        WIDTH // 2,
        478,
        "developer • builder",
        SUB_FONT,
        2,
        WHITE
    )


    # -----------------------------------------
    # SOCIAL ROW
    # -----------------------------------------

    social_y = 540

    social_panel(
        draw,
        435,
        social_y,
        "◎",
        "Instagram"
    )

    social_panel(
        draw,
        545,
        social_y,
        "X",
        "X"
    )

    social_panel(
        draw,
        655,
        social_y,
        "in",
        "LinkedIn"
    )

    social_panel(
        draw,
        765,
        social_y,
        "M",
        "Email"
    )


    # Dividers

    for x in [490, 600, 710]:

        draw.line(
            (
                x,
                social_y - 22,
                x,
                social_y + 22
            ),
            fill=(135, 89, 34, 220),
            width=1
        )


    # -----------------------------------------
    # TECH PANEL
    # -----------------------------------------

    panel_y = 615

    draw.rounded_rectangle(
        (
            410,
            panel_y,
            790,
            panel_y + 42
        ),
        radius=3,
        fill=(4, 4, 4, 190),
        outline=(95, 70, 40, 210),
        width=1
    )

    draw.text(
        (430, panel_y + 9),
        ">",
        font=font(GEORGIA_BOLD, 18),
        fill=GOLD
    )

    text = "software • technology • experiments"

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=SMALL_FONT
    )

    tw = bbox[2] - bbox[0]

    draw.text(
        (
            WIDTH / 2 - tw / 2 + 10,
            panel_y + 13
        ),
        text,
        font=SMALL_FONT,
        fill=WHITE
    )

    return Image.alpha_composite(
        frame,
        overlay
    )


# -------------------------------------------------------
# PROCESS GIF
# -------------------------------------------------------

source = Image.open(INPUT)

frames = []
durations = []

print("Building profile...")

MAX_FRAMES = 72

all_frames = list(ImageSequence.Iterator(source))

# Keep file size sane
step = max(
    1,
    len(all_frames) // MAX_FRAMES
)

selected = all_frames[::step][:MAX_FRAMES]


for index, raw in enumerate(selected):

    print(
        f"Frame {index + 1}/{len(selected)}"
    )

    frame = raw.convert("RGBA")

    frame = cover(
        frame,
        WIDTH,
        HEIGHT
    )

    # Slight cinematic correction

    rgb = frame.convert("RGB")

    rgb = ImageEnhance.Contrast(
        rgb
    ).enhance(1.08)

    rgb = ImageEnhance.Color(
        rgb
    ).enhance(0.92)

    rgb = ImageEnhance.Brightness(
        rgb
    ).enhance(0.88)

    frame = rgb.convert("RGBA")


    frame = add_gradient(frame)

    frame = add_vignette(frame)

    frame = add_grain(frame)

    frame = ui(frame)


    # GIF palette

    frame = frame.convert(
        "P",
        palette=Image.Palette.ADAPTIVE,
        colors=180
    )

    frames.append(frame)


    original_duration = raw.info.get(
        "duration",
        source.info.get(
            "duration",
            80
        )
    )

    durations.append(
        original_duration * step
    )


# -------------------------------------------------------
# SAVE
# -------------------------------------------------------

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=True,
    disposal=2
)

print()
print("DONE")
print(f"Created: {OUTPUT}")
