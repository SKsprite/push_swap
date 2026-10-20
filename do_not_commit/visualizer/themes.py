"""Colour themes. `gradient` is a list of stops, smallest rank first."""

THEMES = {
    "midnight": {
        "bg": "#14161a", "panel": "#1c1f25", "button": "#2a2e36",
        "fg": "#d8dde6", "dim": "#6b7280", "divider": "#333842",
        "highlight": "#ffffff", "select": "#3b82f6",
        "ok": "#4ade80", "ko": "#f87171", "waste": "#4a2a2a",
        "gradient": ["#2850ff", "#8cc88c", "#ff5a28"],
    },
    "light": {
        "bg": "#f6f7f9", "panel": "#ffffff", "button": "#e4e7eb",
        "fg": "#1f2328", "dim": "#8b949e", "divider": "#d0d7de",
        "highlight": "#000000", "select": "#0969da",
        "ok": "#1a7f37", "ko": "#cf222e", "waste": "#ffd8d3",
        "gradient": ["#0969da", "#2da44e", "#e8a317", "#d1242f"],
    },
    "synthwave": {
        "bg": "#1a1033", "panel": "#241645", "button": "#2f1d58",
        "fg": "#f8e9ff", "dim": "#8a6fb0", "divider": "#3b2a63",
        "highlight": "#ffffff", "select": "#ff2e97",
        "ok": "#72f1b8", "ko": "#fe4450", "waste": "#5a1d4a",
        "gradient": ["#36f9f6", "#ff7edb", "#fede5d"],
    },
    "solarized": {
        "bg": "#002b36", "panel": "#073642", "button": "#0d4250",
        "fg": "#93a1a1", "dim": "#586e75", "divider": "#0d4a58",
        "highlight": "#fdf6e3", "select": "#268bd2",
        "ok": "#859900", "ko": "#dc322f", "waste": "#3d2b22",
        "gradient": ["#268bd2", "#2aa198", "#b58900", "#cb4b16"],
    },
    "viridis": {                      # colour-blind friendly
        "bg": "#101418", "panel": "#181d23", "button": "#252b33",
        "fg": "#e6e6e6", "dim": "#6e7681", "divider": "#2b3138",
        "highlight": "#ff4fd8", "select": "#21918c",
        "ok": "#5ec962", "ko": "#ff6b6b", "waste": "#3a2440",
        "gradient": ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"],
    },
    "mono": {
        "bg": "#000000", "panel": "#0d0d0d", "button": "#1f1f1f",
        "fg": "#e0e0e0", "dim": "#707070", "divider": "#2a2a2a",
        "highlight": "#ff3b3b", "select": "#555555",
        "ok": "#ffffff", "ko": "#ff3b3b", "waste": "#3a1a1a",
        "gradient": ["#2a2a2a", "#ffffff"],
    },
}
DEFAULT_THEME = "midnight"


def _rgb(h):
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


def gradient(stops, t):
    """Colour at t in [0, 1] along the stops."""
    t = min(1.0, max(0.0, t))
    seg = t * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    f = seg - i
    a, b = _rgb(stops[i]), _rgb(stops[i + 1])
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * f) for x, y in zip(a, b))
