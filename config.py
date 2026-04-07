"""
============================================================
 config.py
 Constantes globais, paleta de cores, layout e temas.
============================================================
"""

# ─────────────────────────────────────────────
#  JANELA
# ─────────────────────────────────────────────
WIDTH  = 1280
HEIGHT = 720

# Layout base (atualizado ao redimensionar via update_layout())
TOP_BAR_H = 48
SIDE_W    = 200
FOOTER_H  = 32

def update_layout():
    """Recalcula SIDE_W e FOOTER_H proporcionalmente.
    TOP_BAR_H é fixo — a TopBar não escala com a janela.

    DEVE ser chamado sempre que WIDTH/HEIGHT forem alterados:
        cfg.WIDTH, cfg.HEIGHT = new_w, new_h
        cfg.update_layout()
    """
    global TOP_BAR_H, SIDE_W, FOOTER_H
    scale     = WIDTH / 1280.0
    TOP_BAR_H = 48                          # fixo — TopBar não escala
    SIDE_W    = max(140, int(200 * scale))
    FOOTER_H  = max(22,  int(32  * scale))

def root_path(*parts):
    """Retorna caminho relativo à raiz do projeto (onde config.py está)."""
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)

def canvas_rect():
    return (SIDE_W, TOP_BAR_H, WIDTH - SIDE_W, HEIGHT - TOP_BAR_H - FOOTER_H)

def panel_rect():
    """Sem painel separado — retorna rect vazio (canvas inteiro é de desenho)."""
    cax, cay, caw, cah = canvas_rect()
    return (cax, cay, 0, cah)

def draw_rect():
    """Área de desenho = canvas inteiro."""
    return canvas_rect()

def divider_rect():
    return (0, 0, 0, 0)

def set_panel_ratio(ratio):
    pass

# ─────────────────────────────────────────────
#  TEMAS
# ─────────────────────────────────────────────
THEMES = {

    "UNIJUI": {
        "label":       "UNIJUI",
        "swatch":      (0, 82, 165),
        "BG":          (4,  20,  50),
        "BG2":         (8,  35,  78),
        "BG3":         (12, 48, 105),
        "PANEL":       (6,  27,  65),
        "BORDER":      (30, 80, 160),
        "WHITE":       (230, 240, 255),
        "GRAY":        (140, 175, 220),
        "GRAY2":       (70,  110, 170),
        "BLUE":        (80,  160, 255),
        "BLUE_DIM":    (20,  60,  140),
        "GREEN":       (50,  210,  80),
        "GREEN_DIM":   (15,  80,   30),
        "PURPLE":      (180, 130, 255),
        "ORANGE":      (255, 140,  60),
        "CYAN":        (50,  210, 220),
        "YELLOW":      (255, 210,  50),
        "RED":         (255,  75,  75),
        "TAB_ACTIVE":  (0,   82, 165),
        "TAB_HOVER":   (15,  50, 110),
        "TAB_NORMAL":  (6,   27,  65),
        "SIDE_ACTIVE": (0,   82, 165),
        "SIDE_HOVER":  (15,  50, 110),
    },

    "Escuro": {
        "label":       "Escuro",
        "swatch":      (22, 27, 34),
        "BG":          (13,  17,  23),
        "BG2":         (22,  27,  34),
        "BG3":         (28,  35,  50),
        "PANEL":       (18,  24,  32),
        "BORDER":      (48,  54,  61),
        "WHITE":       (255, 255, 255),
        "GRAY":        (139, 148, 158),
        "GRAY2":       (80,  90,  100),
        "BLUE":        (88,  166, 255),
        "BLUE_DIM":    (30,  80,  150),
        "GREEN":       (63,  185,  80),
        "GREEN_DIM":   (20,  80,   30),
        "PURPLE":      (188, 140, 255),
        "ORANGE":      (247, 129, 102),
        "CYAN":        (57,  213, 213),
        "YELLOW":      (227, 179,  65),
        "RED":         (255,  80,  80),
        "TAB_ACTIVE":  (30,  80,  180),
        "TAB_HOVER":   (35,  42,   55),
        "TAB_NORMAL":  (18,  24,   32),
        "SIDE_ACTIVE": (30,  80,  180),
        "SIDE_HOVER":  (35,  45,   60),
    },

    "Claro": {
        "label":       "Claro",
        "swatch":      (220, 235, 255),
        "BG":          (235, 242, 255),
        "BG2":         (210, 225, 248),
        "BG3":         (195, 215, 245),
        "PANEL":       (220, 232, 252),
        "BORDER":      (160, 190, 230),
        "WHITE":       (20,  40,  90),
        "GRAY":        (70,  100, 150),
        "GRAY2":       (120, 150, 190),
        "BLUE":        (0,   82,  165),
        "BLUE_DIM":    (100, 150, 220),
        "GREEN":       (20,  140,  50),
        "GREEN_DIM":   (180, 230, 190),
        "PURPLE":      (110,  60, 200),
        "ORANGE":      (210,  90,  20),
        "CYAN":        (0,   160, 180),
        "YELLOW":      (180, 130,   0),
        "RED":         (200,  30,  30),
        "TAB_ACTIVE":  (0,   82,  165),
        "TAB_HOVER":   (190, 210, 240),
        "TAB_NORMAL":  (220, 232, 252),
        "SIDE_ACTIVE": (0,   82,  165),
        "SIDE_HOVER":  (190, 210, 240),
    },

    "Contraste": {
        "label":       "Contraste",
        "swatch":      (0, 0, 0),
        "BG":          (0,   0,   0),
        "BG2":         (15,  15,  15),
        "BG3":         (25,  25,  25),
        "PANEL":       (10,  10,  10),
        "BORDER":      (255, 255,   0),
        "WHITE":       (255, 255, 255),
        "GRAY":        (200, 200, 200),
        "GRAY2":       (150, 150, 150),
        "BLUE":        (100, 180, 255),
        "BLUE_DIM":    (40,  80,  160),
        "GREEN":       (0,   255,   0),
        "GREEN_DIM":   (0,   80,    0),
        "PURPLE":      (220, 120, 255),
        "ORANGE":      (255, 165,   0),
        "CYAN":        (0,   255, 255),
        "YELLOW":      (255, 255,   0),
        "RED":         (255,   0,   0),
        "TAB_ACTIVE":  (255, 255,   0),
        "TAB_HOVER":   (50,  50,   50),
        "TAB_NORMAL":  (10,  10,   10),
        "SIDE_ACTIVE": (255, 255,   0),
        "SIDE_HOVER":  (50,  50,   50),
    },
}

# ─────────────────────────────────────────────
#  TEMA ATIVO
# ─────────────────────────────────────────────
_current_theme = "UNIJUI"

def apply_theme(name: str):
    global _current_theme
    global BG, BG2, BG3, PANEL, BORDER
    global WHITE, GRAY, GRAY2
    global BLUE, BLUE_DIM, GREEN, GREEN_DIM
    global PURPLE, ORANGE, CYAN, YELLOW, RED
    global TAB_ACTIVE, TAB_HOVER, TAB_NORMAL, SIDE_ACTIVE, SIDE_HOVER

    if name not in THEMES:
        return
    _current_theme = name
    t = THEMES[name]

    BG          = t["BG"]
    BG2         = t["BG2"]
    BG3         = t["BG3"]
    PANEL       = t["PANEL"]
    BORDER      = t["BORDER"]
    WHITE       = t["WHITE"]
    GRAY        = t["GRAY"]
    GRAY2       = t["GRAY2"]
    BLUE        = t["BLUE"]
    BLUE_DIM    = t["BLUE_DIM"]
    GREEN       = t["GREEN"]
    GREEN_DIM   = t["GREEN_DIM"]
    PURPLE      = t["PURPLE"]
    ORANGE      = t["ORANGE"]
    CYAN        = t["CYAN"]
    YELLOW      = t["YELLOW"]
    RED         = t["RED"]
    TAB_ACTIVE  = t["TAB_ACTIVE"]
    TAB_HOVER   = t["TAB_HOVER"]
    TAB_NORMAL  = t["TAB_NORMAL"]
    SIDE_ACTIVE = t["SIDE_ACTIVE"]
    SIDE_HOVER  = t["SIDE_HOVER"]

def current_theme() -> str:
    return _current_theme

# Aplica padrão ao importar
apply_theme("UNIJUI")

# ─────────────────────────────────────────────
#  RESOLUÇÕES
# ─────────────────────────────────────────────
RESOLUTIONS = [
    ("1280 x 720",  (1280,  720)),
    ("1366 x 768",  (1366,  768)),
    ("1600 x 900",  (1600,  900)),
    ("1920 x 1080", (1920, 1080)),
]

# ─────────────────────────────────────────────
#  METADADOS
# ─────────────────────────────────────────────
APP_TITLE   = "UNIJUI - Computacao Grafica"
FOOTER_TEXT = "UNIJUI  .  Computacao Grafica  .  Versao Alfa 0.01"
FPS         = 60

# TAB_H copiado aqui para evitar import circular entre config.py e interface/tabs.py
# Deve ser mantido em sincronia com interface/tabs.py:TAB_H
_TAB_H_DEFAULT = 36

def canvas_rect_tabs():
    """Retorna o canvas rect abaixo da barra de abas (canvas_rect + TAB_H).
    
    BUG-07 FIX: Eliminado import tardio de interface.tabs para evitar
    dependência circular. TAB_H está definido localmente como _TAB_H_DEFAULT.
    """
    x, y, w, h = canvas_rect()
    return (x, y + _TAB_H_DEFAULT, w, h - _TAB_H_DEFAULT)
