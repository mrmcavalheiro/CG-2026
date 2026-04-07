"""
============================================================
 interface/ui.py
 Componentes base de UI reutilizáveis — estilo Windows clássico:
   Button, draw_info_box, draw_label, draw_arrow_line
============================================================
"""

import pygame
import math
import config as cfg

# Paleta Windows (importada para uso local)
WIN_BORDER_LIGHT = (255, 255, 255)
WIN_BORDER_DARK  = (64,  64,  64)
WIN_BORDER_MID   = (128, 128, 128)
WIN_FACE         = (212, 208, 200)


# ─────────────────────────────────────────────
#  BEVEL HELPER
# ─────────────────────────────────────────────
def _bevel_rect(surface, rect, raised=True):
    """Desenha borda biselada Windows em torno de um Rect."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    light = WIN_BORDER_LIGHT if raised else WIN_BORDER_DARK
    dark  = WIN_BORDER_DARK  if raised else WIN_BORDER_LIGHT
    pygame.draw.line(surface, light, (x,   y),   (x+w-1, y),   1)
    pygame.draw.line(surface, light, (x,   y),   (x,   y+h-1), 1)
    pygame.draw.line(surface, dark,  (x+w-1, y), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, dark,  (x, y+h-1), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, WIN_BORDER_MID if raised else WIN_FACE,
                     (x+w-2, y+1), (x+w-2, y+h-2), 1)
    pygame.draw.line(surface, WIN_BORDER_MID if raised else WIN_FACE,
                     (x+1, y+h-2), (x+w-2, y+h-2), 1)


# ─────────────────────────────────────────────
#  BUTTON — estilo Windows clássico
# ─────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, color_active, color_normal, font):
        self.rect          = pygame.Rect(rect)
        self.label         = label
        self.color_active  = color_active
        self.color_normal  = color_normal
        self.font          = font
        self.active        = False
        self.hover         = False
        self._pressed      = False

    def draw(self, surface):
        mx, my = pygame.mouse.get_pos()

        if self.active:
            bg  = self.color_active
            tc  = cfg.WHITE
            off = 0
        elif self.hover:
            bg  = cfg.TAB_HOVER
            tc  = cfg.WHITE
            off = 0
        else:
            bg  = self.color_normal
            tc  = cfg.GRAY
            off = 0

        pygame.draw.rect(surface, bg, self.rect, border_radius=3)
        # Borda apenas quando ativo (destaque sutil) ou hover
        if self.active:
            pygame.draw.rect(surface, cfg.BORDER, self.rect, 1, border_radius=3)
        elif self.hover:
            pygame.draw.rect(surface, cfg.GRAY2, self.rect, 1, border_radius=3)
        txt = self.font.render(self.label, True, tc)
        surface.blit(txt, txt.get_rect(center=(self.rect.centerx + off,
                                               self.rect.centery + off)))

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ─────────────────────────────────────────────
#  INFO BOX — estilo Windows (raised panel)
# ─────────────────────────────────────────────
def draw_info_box(surface, lines, x, y, font, w=320):
    lh = font.get_height() + 4
    h  = len(lines) * lh + 16
    pygame.draw.rect(surface, WIN_FACE, (x, y, w, h), border_radius=2)
    r = pygame.Rect(x, y, w, h)
    _bevel_rect(surface, r, raised=False)
    for i, (text, color) in enumerate(lines):
        surface.blit(font.render(text, True, color),
                     (x + 10, y + 8 + i * lh))


# ─────────────────────────────────────────────
#  LABEL
# ─────────────────────────────────────────────
def draw_label(surface, text, x, y, font, color=None, bg=None):
    color = color or cfg.WHITE
    img   = font.render(text, True, color)
    if bg:
        r = img.get_rect(topleft=(x - 4, y - 2))
        r.inflate_ip(8, 4)
        pygame.draw.rect(surface, bg, r, border_radius=2)
        _bevel_rect(surface, r, raised=True)
    surface.blit(img, (x, y))


# ─────────────────────────────────────────────
#  LINHA COM SETA
# ─────────────────────────────────────────────
def draw_arrow_line(surface, p1, p2, color, width=2, arrow_size=10):
    pygame.draw.line(surface, color, p1, p2, width)
    dx  = p2[0] - p1[0]
    dy  = p2[1] - p1[1]
    ang = math.atan2(dy, dx)
    for da in (-0.4, 0.4):
        ax = p2[0] - arrow_size * math.cos(ang - da)
        ay = p2[1] - arrow_size * math.sin(ang - da)
        pygame.draw.line(surface, color, p2, (ax, ay), width)


# ─────────────────────────────────────────────
#  GRID + EIXOS
# ─────────────────────────────────────────────
def draw_grid(surface, canvas_rect, cx, cy, step=50, color=(30, 38, 48)):
    cx_abs, cy_abs, cw, ch = canvas_rect
    x = cx % step
    while x < cw:
        pygame.draw.line(surface, color, (cx_abs+x, cy_abs), (cx_abs+x, cy_abs+ch))
        x += step
    y = cy % step
    while y < ch:
        pygame.draw.line(surface, color, (cx_abs, cy_abs+y), (cx_abs+cw, cy_abs+y))
        y += step


def draw_axes(surface, canvas_rect, cx, cy, color_x=None, color_y=None, font=None):
    color_x = color_x or cfg.ORANGE
    color_y = color_y or cfg.GREEN
    cx_abs, cy_abs, cw, ch = canvas_rect
    ox = cx_abs + cx
    oy = cy_abs + cy
    pygame.draw.line(surface, color_x, (cx_abs, oy), (cx_abs+cw, oy), 1)
    pygame.draw.polygon(surface, color_x, [
        (cx_abs+cw-2, oy), (cx_abs+cw-10, oy-5), (cx_abs+cw-10, oy+5)])
    pygame.draw.line(surface, color_y, (ox, cy_abs), (ox, cy_abs+ch), 1)
    pygame.draw.polygon(surface, color_y, [
        (ox, cy_abs+2), (ox-5, cy_abs+10), (ox+5, cy_abs+10)])
    if font:
        surface.blit(font.render("X", True, color_x), (cx_abs+cw-16, oy+6))
        surface.blit(font.render("Y", True, color_y), (ox+6, cy_abs+4))


def world_to_screen(pts, canvas_rect, cx, cy):
    cx_abs, cy_abs, _, _ = canvas_rect
    return [(int(cx_abs+cx+p[0]), int(cy_abs+cy-p[1])) for p in pts]


def draw_polygon(surface, pts_screen, color, width=2, fill=None, fill_alpha=60):
    if len(pts_screen) < 3: return
    if fill:
        surf = pygame.Surface(
            (pygame.display.get_surface().get_width(),
             pygame.display.get_surface().get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*fill, fill_alpha), pts_screen)
        surface.blit(surf, (0, 0))
    pygame.draw.polygon(surface, color, pts_screen, width)


# ─────────────────────────────────────────────
#  CODE BOX
# ─────────────────────────────────────────────
_KEYWORDS = {'import','from','as','def','class','return','if','else',
             'elif','for','while','in','not','and','or','True','False',
             'None','lambda','with','pass','break','continue','np'}
_BUILTINS = {'print','len','range','int','float','str','list','dict',
             'array','zeros','ones','dot','transpose','copy'}

_KW_C  = (188, 140, 255)
_BI_C  = (80,  180, 255)
_NUM_C = (247, 129, 102)
_STR_C = (57,  213, 213)
_CMT_C = (100, 140, 100)
_OP_C  = (227, 179,  65)
_DEF_C = (220, 235, 255)

import re as _re
_TOK = _re.compile(
    r'("[^"]*"|\'[^\']*\')'
    r'|(\b\d+\.?\d*\b)'
    r'|([A-Za-z_]\w*)'
    r'|(==|!=|<=|>=|[+\-*/=<>@])'
    r'|(\S)'
)


def _render_code_line(surface, line, x, y, font, max_w):
    stripped = line.lstrip()
    indent_w = font.size(' ')[0] * (len(line) - len(stripped))
    cur_x    = x + indent_w
    if stripped.startswith('#'):
        surface.blit(font.render(line, True, _CMT_C), (x, y))
        return
    prev_end = 0
    for m in _TOK.finditer(stripped):
        tok = m.group(0)
        if   m.group(1): color = _STR_C
        elif m.group(2): color = _NUM_C
        elif m.group(3):
            if   tok in _KEYWORDS: color = _KW_C
            elif tok in _BUILTINS: color = _BI_C
            else:                  color = _DEF_C
        elif m.group(4): color = _OP_C
        else:            color = _DEF_C
        gap = m.start() - prev_end
        if gap > 0: cur_x += font.size(' ')[0] * gap
        prev_end = m.end()
        s = font.render(tok, True, color)
        if cur_x + s.get_width() > x + max_w: break
        surface.blit(s, (cur_x, y))
        cur_x += s.get_width()


def draw_code_box(surface, title, lines, x, y, font, w=320):
    lh = font.get_height() + 3
    h  = 26 + len(lines) * lh + 8
    pygame.draw.rect(surface, WIN_FACE, (x, y, w, h), border_radius=2)
    r = pygame.Rect(x, y, w, h)
    _bevel_rect(surface, r, raised=False)
    pygame.draw.rect(surface, (12, 35, 12), (x, y, w, 22), border_radius=2)
    pygame.draw.rect(surface, cfg.GREEN, (x, y, 3, 22), border_radius=2)
    surface.blit(font.render(title, True, cfg.GREEN), (x+10, y+4))
    pygame.draw.line(surface, WIN_BORDER_MID, (x+4, y+22), (x+w-4, y+22))
    cy_code = y + 28
    for raw_line in lines:
        _render_code_line(surface, raw_line, x+10, cy_code, font, w-20)
        cy_code += lh


# ─────────────────────────────────────────────
#  ALPHA DRAW HELPERS (BUG-01 fix)
#  pygame.draw.line/circle não suportam alpha.
#  Use estas funções para linhas/círculos semi-transparentes.
# ─────────────────────────────────────────────
def draw_line_alpha(surface, color_rgb, p1, p2, width=1, alpha=128):
    """Desenha linha com transparência usando superfície SRCALPHA."""
    surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.line(surf, (*color_rgb[:3], alpha), p1, p2, width)
    surface.blit(surf, (0, 0))


def draw_circle_alpha(surface, color_rgb, center, radius, width=0, alpha=128):
    """Desenha círculo com transparência usando superfície SRCALPHA."""
    surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color_rgb[:3], alpha), center, radius, width)
    surface.blit(surf, (0, 0))
