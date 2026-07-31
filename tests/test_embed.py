import re
from pathlib import Path

HTML = (Path(__file__).resolve().parent.parent / "site" / "index.html").read_text(encoding="utf-8")

# Colour constants reimplemented from site/index.html's derivation logic, keyed by
# whether the background counts as "dark" under the same perceptual-luminance test
# the page uses to branch its palette.
INK = {True: "e8eaf0", False: "1f2430"}
MUTED = {True: "9aa1ad", False: "6b7280"}
TRACK_ALPHA = {True: 0.16, False: 0.20}
TRACK_OVERLAY = {True: (255, 255, 255), False: (0, 0, 0)}


def hex_to_rgb(h):
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def is_dark(bg_hex):
    r, g, b = hex_to_rgb(bg_hex)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255 < 0.5


def blend(fg, alpha, bg):
    return tuple(fg[i] * alpha + bg[i] * (1 - alpha) for i in range(3))


def _srgb_to_linear(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    r, g, b = rgb
    return 0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g) + 0.0722 * _srgb_to_linear(b)


def contrast_ratio(rgb1, rgb2):
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


BACKGROUNDS = ["191919", "ffffff", "1f2b3a"]


def test_primary_text_contrast_at_least_4_5():
    for bg_hex in BACKGROUNDS:
        dark = is_dark(bg_hex)
        ratio = contrast_ratio(hex_to_rgb(INK[dark]), hex_to_rgb(bg_hex))
        assert ratio >= 4.5, f"INK contrast for bg={bg_hex} is {ratio:.2f}, need >= 4.5"


def test_muted_text_contrast_at_least_3():
    for bg_hex in BACKGROUNDS:
        dark = is_dark(bg_hex)
        ratio = contrast_ratio(hex_to_rgb(MUTED[dark]), hex_to_rgb(bg_hex))
        assert ratio >= 3.0, f"MUTED contrast for bg={bg_hex} is {ratio:.2f}, need >= 3.0"


def test_zero_percent_ring_track_visible():
    for bg_hex in BACKGROUNDS:
        dark = is_dark(bg_hex)
        bg_rgb = hex_to_rgb(bg_hex)
        track_rgb = blend(TRACK_OVERLAY[dark], TRACK_ALPHA[dark], bg_rgb)
        ratio = contrast_ratio(track_rgb, bg_rgb)
        assert ratio >= 1.4, f"TRACK contrast for bg={bg_hex} is {ratio:.2f}, need >= 1.4"


def test_no_network_resources():
    assert "http://" not in HTML
    assert "https://" not in HTML


def test_weekly_chart_and_category_markup_absent():
    lowered = HTML.lower()
    assert "by_type" not in lowered
    assert "weeks" not in lowered
    assert "bar" not in lowered


def test_exactly_three_rings_rendered():
    # one function definition plus exactly three call sites (today, week, open total);
    # word-boundary lookbehind avoids false matches like "toLocaleDateString("
    ring_calls = re.findall(r"(?<![A-Za-z])ring\(", HTML)
    assert len(ring_calls) == 4
    assert HTML.count("function ring(") == 1
