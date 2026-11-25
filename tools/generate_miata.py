from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "assets" / "miata.gif"

CANVAS_WIDTH = 960
CANVAS_HEIGHT = 430
SUPERSAMPLE = 2
FONT_SIZE = 15 * SUPERSAMPLE
LINE_HEIGHT = 18 * SUPERSAMPLE
MARGIN_X = 24 * SUPERSAMPLE
BOX_WIDTH = 96

BG = (5, 11, 7)
SCANLINE = (8, 20, 12)
DIM = (18, 62, 32)
MUTED = (0, 120, 52)
PRIMARY = (0, 255, 65)
ACCENT = (92, 255, 140)
BRIGHT = (190, 255, 205)

PALETTE_COLORS = (BG, SCANLINE, DIM, MUTED, PRIMARY, ACCENT, BRIGHT)

FONT_CANDIDATES = (
    "DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
)

FRAME_SPECS = (
    {
        "label": "HEADLIGHTS DOWN",
        "state": "down",
        "blink": "steady",
        "beams": "off",
        "duration": 780,
    },
    {
        "label": "POWERING UP",
        "state": "quarter",
        "blink": "steady",
        "beams": "off",
        "duration": 420,
    },
    {
        "label": "HEADLIGHTS UP",
        "state": "half",
        "blink": "steady",
        "beams": "off",
        "duration": 420,
    },
    {
        "label": "HEADLIGHTS UP",
        "state": "up",
        "blink": "steady",
        "beams": "off",
        "duration": 780,
    },
    {
        "label": "NIGHT MODE",
        "state": "up",
        "blink": "on",
        "beams": "on",
        "duration": 420,
    },
    {
        "label": "NIGHT MODE",
        "state": "up",
        "blink": "off",
        "beams": "off",
        "duration": 170,
    },
    {
        "label": "NIGHT MODE",
        "state": "up",
        "blink": "on",
        "beams": "on",
        "duration": 420,
    },
    {
        "label": "RETURN TO NORMAL",
        "state": "half",
        "blink": "steady",
        "beams": "off",
        "duration": 420,
    },
)

CAR_TEMPLATE = (
    "                         _______________________________",
    "                    ____/                               \\____",
    "               ____/                                         \\____",
    "          ____/                                                   \\____",
    "     ____/                                                       @HL0@\\____@B0@",
    " ___/                                                            @HL1@ \\___@B1@",
    "/                                                                @HL2@     \\@B2@",
    "|          _________        _/\\                   _________         |",
    "\\         /         \\      |  |                 /         \\        /",
    " \\_______/           \\_____|__|________________/           \\_______/",
    "           (   O   )                             (   O   )",
)


def load_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, FONT_SIZE)
        except OSError:
            continue
    return ImageFont.load_default(size=FONT_SIZE)


def terminal_box(title: str, rows: tuple[str, ...] | list[str], width: int) -> list[str]:
    prefix = f"+--[ {title} ]"
    top = prefix + "-" * max(0, width - len(prefix) - 1) + "+"
    body = [f"| {row.ljust(width - 4)} |" for row in rows]
    return [top, *body, "+" + "-" * (width - 2) + "+"]


def headlight_block(state: str, blink: str, row: int) -> str:
    if state == "down":
        return ("[  ][  ]", "[..][..]", "[__][__]")[row]
    if state == "quarter":
        return ("[==][==]", "[  ][  ]", "[__][__]")[row]
    if state == "half":
        return ("[##][##]", "[==][==]", "[  ][  ]")[row]
    if blink == "on":
        return ("[@@][@@]", "[@@][@@]", "[@@][@@]")[row]
    if blink == "off":
        return ("[++][++]", "[++][++]", "[++][++]")[row]
    return ("[##][##]", "[##][##]", "[##][##]")[row]


def beam_block(mode: str) -> tuple[str, str, str]:
    if mode == "on":
        return ("  \\    \\", "   \\  \\ ", "  /    /")
    return ("        ", "        ", "        ")


def progress_bar(index: int, total: int) -> str:
    return "[" + "#" * (index + 1) + "-" * (total - index - 1) + "]"


def build_frame_lines(spec: dict, index: int, total: int) -> list[str]:
    header = terminal_box(
        "GARAGE://MX-5_NA",
        (
            "IDENTITY : SUENO OCHO   ROLE : STUDENT",
            "STATUS : ENDLESS ERRORS   MINDSET : CONTROL IS ALL I NEED!!",
            f"FRAME : {index + 1:02d}/{total:02d}   VEHICLE : MAZDA MX-5 NA",
        ),
        BOX_WIDTH,
    )
    beams = beam_block(spec["beams"])
    car = []
    for row, template_line in enumerate(CAR_TEMPLATE):
        line = template_line
        if row in (4, 5, 6):
            line = line.replace(f"@HL{row - 4}@", headlight_block(spec["state"], spec["blink"], row - 4))
        line = line.replace("@B0@", beams[0])
        line = line.replace("@B1@", beams[1])
        line = line.replace("@B2@", beams[2])
        car.append(line.ljust(BOX_WIDTH))
    status = (
        f"> headlight_sequence : {spec['label'].lower().ljust(18)} {progress_bar(index, total)}",
        f"> mode : {spec['beams'].upper().ljust(7)}  loop : INFINITE  signal : {spec['blink'].upper()}",
    )
    return [*header, "", *car, "", *status]


def char_color(char: str) -> tuple[int, int, int]:
    if char in "@#*":
        return BRIGHT
    if char in "+=":
        return ACCENT
    if char in ">O":
        return PRIMARY
    if char in " |/\\_":
        return MUTED
    if char in ".,-()[]:":
        return DIM
    return MUTED


def draw_ascii(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> int:
    char_width = font.getlength("M")
    text_width = BOX_WIDTH * char_width
    start_x = (CANVAS_WIDTH * SUPERSAMPLE - text_width) / 2
    start_y = (CANVAS_HEIGHT * SUPERSAMPLE - len(lines) * LINE_HEIGHT) / 2
    for row, line in enumerate(lines):
        y = start_y + row * LINE_HEIGHT
        for column, char in enumerate(line):
            if char == " ":
                continue
            x = start_x + column * char_width
            draw.text((x, y), char, font=font, fill=char_color(char))
    return char_width


def render_frame(spec: dict, index: int, total: int) -> Image.Image:
    width = CANVAS_WIDTH * SUPERSAMPLE
    height = CANVAS_HEIGHT * SUPERSAMPLE
    base = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(base)
    draw.rectangle(
        (12 * SUPERSAMPLE, 12 * SUPERSAMPLE, width - 12 * SUPERSAMPLE, height - 12 * SUPERSAMPLE),
        outline=MUTED,
        width=SUPERSAMPLE,
    )
    for y in range(0, height, 4 * SUPERSAMPLE):
        draw.line((0, y, width, y), fill=SCANLINE, width=SUPERSAMPLE)

    font = load_font()
    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    draw_ascii(text_draw, build_frame_lines(spec, index, total), font)

    glow = text_layer.filter(ImageFilter.GaussianBlur(2 * SUPERSAMPLE))
    glow.putalpha(glow.getchannel("A").point(lambda alpha: int(alpha * 0.38)))
    base = Image.alpha_composite(base.convert("RGBA"), glow)
    base = Image.alpha_composite(base, text_layer)
    return base.convert("RGB").resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS)


def build_palette() -> Image.Image:
    palette = Image.new("P", (1, 1))
    values = [component for color in PALETTE_COLORS for component in color]
    values.extend([0] * (768 - len(values)))
    palette.putpalette(values)
    return palette


def save_gif(frames: list[Image.Image], output: Path) -> None:
    palette = build_palette()
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    durations = [spec["duration"] for spec in FRAME_SPECS]
    output.parent.mkdir(parents=True, exist_ok=True)
    quantized[0].save(
        output,
        save_all=True,
        append_images=quantized[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the animated ASCII Mazda MX-5 NA GIF.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="GIF output path")
    parser.add_argument("--preview", type=int, choices=range(1, len(FRAME_SPECS) + 1), help="print a frame as ASCII")
    args = parser.parse_args()

    if args.preview is not None:
        index = args.preview - 1
        print("\n".join(build_frame_lines(FRAME_SPECS[index], index, len(FRAME_SPECS))))
        return

    frames = [
        render_frame(spec, index, len(FRAME_SPECS))
        for index, spec in enumerate(FRAME_SPECS)
    ]
    save_gif(frames, args.output)
    print(f"generated {args.output} ({len(frames)} frames, {CANVAS_WIDTH}x{CANVAS_HEIGHT})")


if __name__ == "__main__":
    main()
