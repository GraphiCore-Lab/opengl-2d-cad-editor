# ── Pencere Ayarları ─────────────────────────────

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

# Alias
WIDTH = WINDOW_WIDTH
HEIGHT = WINDOW_HEIGHT

TITLE = "Mini CAD Editor"
FPS = 60


# ── Renkler RGB 0-255 ────────────────────────────

COLOR_BG = (30, 30, 30)
COLOR_CANVAS = (40, 40, 40)
COLOR_GRID = (70, 70, 70)
COLOR_GRID_MAJOR = (95, 95, 95)

COLOR_SELECTION = (255, 180, 0)
COLOR_PREVIEW = (0, 180, 255)

COLOR_UI_PANEL = (235, 235, 235)
COLOR_UI_BUTTON = (210, 210, 210)
COLOR_UI_BUTTON_ACTIVE = (140, 190, 255)
COLOR_UI_BORDER = (60, 60, 60)


# ── Layout UI ────────────────────────────────────

TOOLBAR_HEIGHT = 92
PROPERTIES_PANEL_WIDTH = 220
STATUS_BAR_HEIGHT = 30

CANVAS_X = 0
CANVAS_Y = TOOLBAR_HEIGHT

CANVAS_W = WINDOW_WIDTH - PROPERTIES_PANEL_WIDTH
CANVAS_H = WINDOW_HEIGHT - STATUS_BAR_HEIGHT

# Eski isim kullanan dosyalar için alias
CANVAS_WIDTH = CANVAS_W
CANVAS_HEIGHT = CANVAS_H


# ── Çizim Ayarları ───────────────────────────────

DEFAULT_STROKE_COLOR = (0.0, 0.0, 0.0)
DEFAULT_FILL_COLOR = (0.8, 0.8, 0.8)
DEFAULT_LINE_WIDTH = 2


# ── Grid / Snap ──────────────────────────────────

GRID_SIZE = 20
SNAP_ENABLED = True
SNAP_THRESHOLD = 10


# ── Hit Test Selection ───────────────────────────

HIT_THRESHOLD = 10


# ── Tool Sabitleri ───────────────────────────────

TOOL_SELECT = "select"
TOOL_LINE = "line"
TOOL_RECT = "rect"
TOOL_CIRCLE = "circle"
TOOL_MOVE = "move"
TOOL_ROTATE = "rotate"
TOOL_SCALE = "scale"
TOOL_TRIANGLE = "triangle"

# ── File Save / Load ─────────────────────────────

DEFAULT_SAVE_PATH = "scene.json"