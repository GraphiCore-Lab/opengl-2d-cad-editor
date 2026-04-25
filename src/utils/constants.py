# ── Pencere ──────────────────────────────────────────────────
WIDTH  = 1280
HEIGHT = 720
TITLE  = "OpenGL 2D CAD"
FPS    = 60

# ── UI Panel genişlikleri ────────────────────────────────────
TOOLBAR_WIDTH   = 60    # sol ikon toolbar
PROPS_WIDTH     = 200   # sağ properties paneli
STATUSBAR_HEIGHT = 24   # alt durum çubuğu

# Canvas'ın gerçek başladığı x koordinatı
CANVAS_X = TOOLBAR_WIDTH
CANVAS_W = WIDTH - TOOLBAR_WIDTH - PROPS_WIDTH
CANVAS_H = HEIGHT - STATUSBAR_HEIGHT

# ── Renkler (R, G, B) 0-255 ──────────────────────────────────
COLOR_BG          = (30,  30,  30)
COLOR_CANVAS      = (45,  45,  45)
COLOR_TOOLBAR_BG  = (25,  25,  25)
COLOR_PROPS_BG    = (35,  35,  35)
COLOR_GRID        = (60,  60,  60)
COLOR_SELECTION   = (0,   180, 255)
COLOR_TEXT        = (220, 220, 220)
COLOR_BTN_ACTIVE  = (0,   120, 200)
COLOR_BTN_HOVER   = (70,  70,  70)
COLOR_BTN_NORMAL  = (50,  50,  50)

# ── Grid ──────────────────────────────────────────────────────
GRID_SIZE     = 20      # piksel araları
SNAP_ENABLED  = True
SNAP_THRESHOLD = 10     # snap mesafesi (piksel)

# ── Tool isimleri ─────────────────────────────────────────────
TOOL_SELECT    = "select"
TOOL_LINE      = "line"
TOOL_RECT      = "rect"
TOOL_CIRCLE    = "circle"
TOOL_MOVE      = "move"
TOOL_ROTATE    = "rotate"
TOOL_SCALE     = "scale"

# ── Seçim ────────────────────────────────────────────────────
HIT_THRESHOLD = 8       # tıklama toleransı (piksel)

# ── Dosya ────────────────────────────────────────────────────
DEFAULT_SAVE_PATH = "scene.json"