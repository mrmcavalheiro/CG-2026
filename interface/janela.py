"""
============================================================
 interface/janela.py
 Sistema de janelas flutuantes estilo Windows clássico.

 NOVIDADES:
   - Scrollbar vertical nas janelas flutuantes
   - Fonte escala automaticamente com o tamanho da janela
   - Fundo da área cliente escuro (cfg.BG2)
   - Borda biselada Windows (3 camadas)
   - Botões ─ □ ✕ estilo Win32
   - Gradiente azul na titlebar
============================================================
"""

import pygame
import config as cfg

# ─── Constantes estilo Windows ───────────────────────────
TITLE_H       = 28
BTN_W         = 22
BTN_H         = 20
BTN_PAD       = 3
BORDER_W      = 3
RESIZE_BORDER = 6
MIN_W         = 140
MIN_H         = 60
SHADOW_OFF    = 4
SB_W          = 10   # largura da scrollbar interna

# Paleta Windows
WIN_TITLE_ACTIVE1  = (10,  36, 106)
WIN_TITLE_ACTIVE2  = (166, 202, 240)
WIN_TITLE_INACTIVE = (128, 128, 128)
WIN_BORDER_LIGHT   = (255, 255, 255)
WIN_BORDER_DARK    = (64,  64,  64)
WIN_BORDER_MID     = (128, 128, 128)
WIN_BORDER_FACE    = (212, 208, 200)
WIN_TITLE_TEXT     = (255, 255, 255)
WIN_BTN_FACE       = (212, 208, 200)
WIN_BTN_HOVER      = (232, 228, 220)
WIN_BTN_CLOSE_HOV  = (200,  40,  40)
WIN_SHADOW         = (0,   0,   0,  60)

_FONT_BASE_SZ = 13
_FONT_REF_H   = 200
_FONT_MIN_SZ  = 13
_FONT_MAX_SZ  = 28

_font_cache = {}

def _get_scaled_font(win_h):
    if win_h <= _FONT_REF_H:
        size = _FONT_BASE_SZ
    else:
        ratio = win_h / _FONT_REF_H
        size  = int(_FONT_BASE_SZ * ratio)
        size  = min(size, _FONT_MAX_SZ)
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont("monospace", size)
    return _font_cache[size]


class FloatWindow:
    def __init__(self, title, x, y, w, h,
                 color=None, closable=True, resizable=True):
        self.title     = title
        self.x         = float(x)
        self.y         = float(y)
        self.w         = float(w)
        self.h         = float(h)
        self.color     = color or cfg.BLUE
        self.closable  = closable
        self.resizable = resizable

        self.visible    = True
        self.minimized  = False
        self.maximized  = False

        self._prev_x = x; self._prev_y = y
        self._prev_w = w; self._prev_h = h

        self._dragging    = False
        self._drag_off    = (0, 0)
        self._resizing    = False
        self._resize_edge = None
        self._resize_orig = None

        self.focused = False

        # ── Scroll interno ────────────────────────────────
        self._scroll     = 0      # posição atual (px)
        self._max_scroll = 0      # calculado pelo draw_rows_in_win
        self._sb_dragging   = False
        self._sb_drag_start = 0

    # ── Fonte escalada desta janela ───────────────────────
    @property
    def font(self):
        return _get_scaled_font(self.h)

    @property
    def line_height(self):
        return self.font.get_height() + 4

    # ── Geometria ─────────────────────────────────────────
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y),
                           int(self.w), int(self.h))

    @property
    def title_rect(self):
        return pygame.Rect(int(self.x), int(self.y),
                           int(self.w), TITLE_H)

    @property
    def content_rect(self):
        """Área cliente — reserva espaço para a scrollbar interna."""
        if self.minimized:
            return pygame.Rect(int(self.x), int(self.y) + TITLE_H, 0, 0)
        bw = BORDER_W
        return pygame.Rect(
            int(self.x) + bw,
            int(self.y) + TITLE_H,
            int(self.w) - bw * 2 - SB_W - 2,   # ← reserva espaço para SB
            int(self.h) - TITLE_H - bw
        )

    @property
    def _sb_track_rect(self):
        """Faixa da scrollbar (direita da área cliente)."""
        bw = BORDER_W
        return pygame.Rect(
            int(self.x) + int(self.w) - bw - SB_W - 1,
            int(self.y) + TITLE_H + 2,
            SB_W,
            int(self.h) - TITLE_H - bw - 4
        )

    def _btn_rects(self):
        right = int(self.x + self.w) - BORDER_W - BTN_PAD
        by    = int(self.y) + (TITLE_H - BTN_H) // 2
        close = pygame.Rect(right - BTN_W,               by, BTN_W, BTN_H)
        maxi  = pygame.Rect(right - BTN_W*2 - BTN_PAD,   by, BTN_W, BTN_H)
        mini  = pygame.Rect(right - BTN_W*3 - BTN_PAD*2, by, BTN_W, BTN_H)
        return close, mini, maxi

    def _resize_edge_at(self, pos):
        if self.minimized or self.maximized or not self.resizable:
            return None
        rx, ry, rw, rh = self.rect
        mx, my = pos
        in_r  = abs(mx - (rx+rw)) < RESIZE_BORDER and ry < my < ry+rh
        in_b  = abs(my - (ry+rh)) < RESIZE_BORDER and rx < mx < rx+rw
        in_rb = (abs(mx-(rx+rw)) < RESIZE_BORDER*2 and
                 abs(my-(ry+rh)) < RESIZE_BORDER*2)
        if in_rb: return 'rb'
        if in_r:  return 'r'
        if in_b:  return 'b'
        return None

    # ── Scroll ────────────────────────────────────────────
    def scroll_by(self, dy_lines):
        """Rola N linhas (positivo = baixo, negativo = cima)."""
        step = self.line_height * 3
        self._scroll = max(0, min(self._max_scroll,
                                  self._scroll + dy_lines * step))

    def _sb_thumb_rect(self):
        tr = self._sb_track_rect
        if self._max_scroll <= 0:
            return pygame.Rect(tr.x, tr.y, tr.w, tr.h)
        content_h = tr.h + self._max_scroll
        ratio  = tr.h / max(content_h, 1)
        sb_h   = max(20, int(tr.h * ratio))
        travel = tr.h - sb_h
        sb_y   = tr.y + int(travel * self._scroll / max(self._max_scroll, 1))
        return pygame.Rect(tr.x, sb_y, tr.w, sb_h)

    def hit_scrollbar(self, pos):
        return self._sb_track_rect.collidepoint(pos) and not self.minimized

    def start_sb_drag(self, pos):
        self._sb_dragging   = True
        thumb = self._sb_thumb_rect()
        self._sb_drag_start = pos[1] - thumb.y

    def do_sb_drag(self, pos):
        if not self._sb_dragging:
            return
        tr  = self._sb_track_rect
        thumb = self._sb_thumb_rect()
        travel = tr.h - thumb.h
        if travel <= 0:
            return
        new_y  = pos[1] - self._sb_drag_start
        ratio  = max(0.0, min(1.0, (new_y - tr.y) / travel))
        self._scroll = int(ratio * self._max_scroll)

    def stop_sb_drag(self):
        self._sb_dragging = False

    # ── Ações ─────────────────────────────────────────────
    def close(self):           self.visible   = False
    def toggle_minimize(self):
        self.minimized = not self.minimized; self.maximized = False

    def toggle_maximize(self, canvas_rect):
        if self.maximized:
            self.x, self.y = self._prev_x, self._prev_y
            self.w, self.h = self._prev_w, self._prev_h
            self.maximized = False
        else:
            self._prev_x, self._prev_y = self.x, self.y
            self._prev_w, self._prev_h = self.w, self.h
            cx, cy, cw, ch = canvas_rect
            self.x, self.y = cx, cy
            self.w, self.h = cw, ch
            self.maximized = True; self.minimized = False

    # ── Draw ──────────────────────────────────────────────
    def draw_background(self, surface):
        if not self.visible: return
        ix, iy = int(self.x), int(self.y)
        iw, ih = int(self.w), int(self.h)
        vis_h  = TITLE_H if self.minimized else ih

        # sombra
        if not self.maximized:
            s = pygame.Surface((iw+SHADOW_OFF, vis_h+SHADOW_OFF), pygame.SRCALPHA)
            s.fill(WIN_SHADOW)
            surface.blit(s, (ix+SHADOW_OFF, iy+SHADOW_OFF))

        if not self.minimized:
            pygame.draw.rect(surface, cfg.BG2, (ix, iy, iw, ih))
            pygame.draw.rect(surface, cfg.BORDER,
                             (ix+BORDER_W, iy+TITLE_H, iw-BORDER_W*2, ih-TITLE_H-BORDER_W), 1)

        _draw_bevel(surface, ix, iy, iw, vis_h)

    def _draw_scrollbar(self, surface):
        """Desenha a scrollbar interna (sempre visível quando há conteúdo)."""
        if self.minimized or self.maximized:
            return
        tr = self._sb_track_rect
        # Fundo da trilha
        pygame.draw.rect(surface, cfg.BG3, tr, border_radius=4)
        pygame.draw.rect(surface, cfg.BORDER, tr, 1, border_radius=4)

        if self._max_scroll > 0:
            thumb = self._sb_thumb_rect()
            col = cfg.BLUE if self._sb_dragging else (80, 130, 200)
            pygame.draw.rect(surface, col, thumb, border_radius=4)
            pygame.draw.rect(surface, (150, 200, 255), thumb, 1, border_radius=4)
        else:
            # Trilha desabilitada — thumb ocupa tudo
            thumb = pygame.Rect(tr.x+1, tr.y+1, tr.w-2, tr.h-2)
            pygame.draw.rect(surface, cfg.BG2, thumb, border_radius=3)

    def draw_titlebar(self, surface, fonts, focused=False):
        if not self.visible: return
        ix, iy = int(self.x), int(self.y)
        iw     = int(self.w)

        _draw_titlebar_gradient(surface,
                                ix+BORDER_W, iy+BORDER_W,
                                iw-BORDER_W*2, TITLE_H-BORDER_W,
                                focused)

        icon_x = ix + BORDER_W + 4
        icon_y = iy + BORDER_W + (TITLE_H - BORDER_W - 14) // 2
        _draw_system_icon(surface, icon_x, icon_y)

        close_r, min_r, max_r = self._btn_rects()
        max_title_w = close_r.x - (ix + BORDER_W + 24) - 8
        tc    = WIN_TITLE_TEXT if focused else (200, 200, 200)
        font  = fonts['sm']
        ts    = self.title
        while ts and font.size(ts + '...')[0] > max_title_w:
            ts = ts[:-1]
        if ts != self.title: ts += '...'
        t_surf = font.render(ts, True, tc)
        ty     = iy + BORDER_W + (TITLE_H - BORDER_W - t_surf.get_height()) // 2
        surface.blit(t_surf, (ix + BORDER_W + 22, ty))

        _draw_win_btn(surface, min_r, 'min',   focused)
        _draw_win_btn(surface, max_r, 'max' if not self.maximized else 'restore', focused)
        if self.closable:
            _draw_win_btn(surface, close_r, 'close', focused)
        else:
            _draw_win_btn(surface, close_r, 'close_dis', focused)

        if self.resizable and not self.minimized and not self.maximized:
            _draw_resize_grip(surface, ix+iw-15, iy+int(self.h)-15)

    def draw(self, surface, fonts, focused=False):
        self.draw_background(surface)
        self.draw_titlebar(surface, fonts, focused)

    # ── Eventos ───────────────────────────────────────────
    def hit_title(self, pos):
        if not self.visible: return False
        close_r, min_r, max_r = self._btn_rects()
        return (self.title_rect.collidepoint(pos) and
                not close_r.collidepoint(pos) and
                not min_r.collidepoint(pos) and
                not max_r.collidepoint(pos))

    def hit_any(self, pos):
        if not self.visible: return False
        if self.minimized:   return self.title_rect.collidepoint(pos)
        return self.rect.collidepoint(pos)

    def click_buttons(self, pos, canvas_rect):
        if not self.visible: return False
        close_r, min_r, max_r = self._btn_rects()
        if self.closable and close_r.collidepoint(pos):
            self.close(); return True
        if min_r.collidepoint(pos):
            self.toggle_minimize(); return True
        if max_r.collidepoint(pos):
            self.toggle_maximize(canvas_rect); return True
        return False

    def start_drag(self, pos):
        if self.maximized: return
        self._dragging = True
        self._drag_off = (pos[0]-self.x, pos[1]-self.y)

    def start_resize(self, pos):
        edge = self._resize_edge_at(pos)
        if edge:
            self._resizing    = True
            self._resize_edge = edge
            self._resize_orig = (pos[0], pos[1], self.w, self.h)
            return True
        return False

    def do_drag(self, pos, canvas_rect):
        if not self._dragging: return
        cx, cy, cw, ch = canvas_rect
        nx = max(cx, min(pos[0]-self._drag_off[0], cx+cw-self.w))
        ny = max(cy, min(pos[1]-self._drag_off[1], cy+ch-TITLE_H))
        self.x, self.y = nx, ny

    def do_resize(self, pos):
        if not self._resizing: return
        mx0, my0, w0, h0 = self._resize_orig
        dx = pos[0]-mx0; dy = pos[1]-my0
        if 'r' in self._resize_edge: self.w = max(MIN_W, w0+dx)
        if 'b' in self._resize_edge: self.h = max(MIN_H, h0+dy)

    def stop_drag_resize(self):
        self._dragging = False; self._resizing = False; self._resize_edge = None

    def cursor_for(self, pos):
        if not self.visible or self.minimized or self.maximized: return None
        edge = self._resize_edge_at(pos)
        if edge == 'rb': return pygame.SYSTEM_CURSOR_SIZENWSE
        if edge == 'r':  return pygame.SYSTEM_CURSOR_SIZEWE
        if edge == 'b':  return pygame.SYSTEM_CURSOR_SIZENS
        if self.hit_title(pos): return pygame.SYSTEM_CURSOR_HAND
        return None

    def content_clip(self, surface):
        return _ContentCtx(self, surface)


class _ContentCtx:
    def __init__(self, win, surface):
        self.win = win; self.surface = surface
        cr = win.content_rect
        self.rect = (cr.x, cr.y, cr.w, cr.h)
        self._old_clip = surface.get_clip()
        surface.set_clip(cr)

    def __enter__(self):    return self.rect
    def __exit__(self, *_): self.surface.set_clip(self._old_clip)
    # WARN-02 FIX: done() removido — usar apenas context manager 'with win.content_clip()'


# ─────────────────────────────────────────────
#  WINDOW MANAGER
# ─────────────────────────────────────────────
class WindowManager:
    def __init__(self, canvas_rect_fn):
        self._cr_fn   = canvas_rect_fn
        self._windows = []
        self._active  = None

    def create(self, title, x, y, w, h, color=None, closable=True, resizable=True):
        cx, cy, cw, ch = self._cr_fn()
        w = min(w, cw)
        h = min(h, ch - TITLE_H)
        x = max(cx, min(x, cx + cw - w))
        y = max(cy, min(y, cy + ch - TITLE_H))
        win = FloatWindow(title, x, y, w, h, color=color,
                          closable=closable, resizable=resizable)
        self._windows.append(win)
        return win

    def bring_to_front(self, win):
        if win in self._windows:
            self._windows.remove(win); self._windows.append(win)

    def top_window(self):
        for w in reversed(self._windows):
            if w.visible: return w
        return None

    def _window_at(self, pos):
        """Janela visível mais ao topo que contém pos."""
        for w in reversed(self._windows):
            if w.visible and w.hit_any(pos):
                return w
        return None

    def draw_backgrounds(self, surface):
        for win in self._windows:
            win.draw_background(surface)

    def draw_titlebars(self, surface, fonts):
        top = self.top_window()
        for win in self._windows:
            win.draw_titlebar(surface, fonts, focused=(win is top))

    def draw(self, surface, fonts):
        top = self.top_window()
        for win in self._windows:
            win.draw(surface, fonts, focused=(win is top))

    def draw_managed(self, surface, fonts, content_fn):
        """
        Desenha todas as janelas com z-order correto:
          1. fundo + borda
          2. conteúdo (via content_fn) com clipping
          3. scrollbar por cima do conteúdo
          4. titlebar por cima de tudo
        """
        cx, cy, cw, ch = self._cr_fn()
        for win in self._windows:
            if not win.visible: continue
            win.w = min(win.w, cw)
            win.h = min(win.h, ch - TITLE_H)
            win.x = max(cx, min(win.x, cx + cw - win.w))
            win.y = max(cy, min(win.y, cy + ch - TITLE_H))

        top = self.top_window()
        for win in self._windows:
            if not win.visible:
                continue
            focused = (win is top)
            # 1. fundo
            win.draw_background(surface)
            # 2. conteúdo com clipping
            if not win.minimized:
                old_clip = surface.get_clip()
                surface.set_clip(win.content_rect)
                try:
                    content_fn(win, surface)
                finally:
                    surface.set_clip(old_clip)
            # 3. scrollbar (por cima do conteúdo, fora do clip)
            win._draw_scrollbar(surface)
            # 4. titlebar
            win.draw_titlebar(surface, fonts, focused=focused)

    def handle_mouse_down(self, pos):
        cr = self._cr_fn()
        for win in reversed(self._windows):
            if not win.visible: continue
            # Scrollbar tem prioridade
            if win.hit_scrollbar(pos) and not win.minimized:
                win.start_sb_drag(pos)
                self._active = win
                self.bring_to_front(win)
                return True
            if win.click_buttons(pos, cr):
                self.bring_to_front(win); return True
            if win.start_resize(pos):
                self._active = win; self.bring_to_front(win); return True
            if win.hit_title(pos):
                win.start_drag(pos); self._active = win
                self.bring_to_front(win); return True
            if win.hit_any(pos):
                self.bring_to_front(win); return True
        return False

    def handle_mouse_move(self, pos):
        if self._active:
            if self._active._sb_dragging:   self._active.do_sb_drag(pos)
            elif self._active._dragging:     self._active.do_drag(pos, self._cr_fn())
            elif self._active._resizing:     self._active.do_resize(pos)
            return True
        for win in reversed(self._windows):
            if not win.visible: continue
            cur = win.cursor_for(pos)
            if cur is not None:
                pygame.mouse.set_cursor(cur); return False
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return False

    def handle_mouse_up(self, pos):
        if self._active:
            self._active.stop_drag_resize()
            self._active.stop_sb_drag()
            self._active = None

    def handle_scroll(self, pos, dy):
        """Encaminha scroll para a janela sob o cursor."""
        win = self._window_at(pos)
        if win:
            win.scroll_by(-dy)   # dy>0 = roda para cima = scroll down
            return True
        return False


# ─────────────────────────────────────────────
#  HELPERS DE DESENHO — ESTILO WINDOWS
# ─────────────────────────────────────────────

def _draw_bevel(surface, x, y, w, h):
    pygame.draw.line(surface, WIN_BORDER_LIGHT, (x,   y),   (x+w-1, y),   1)
    pygame.draw.line(surface, WIN_BORDER_LIGHT, (x,   y),   (x,   y+h-1), 1)
    pygame.draw.line(surface, WIN_BORDER_DARK,  (x+w-1, y), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, WIN_BORDER_DARK,  (x, y+h-1), (x+w-1, y+h-1), 1)

    pygame.draw.line(surface, WIN_BORDER_FACE, (x+1, y+1), (x+w-2, y+1),   1)
    pygame.draw.line(surface, WIN_BORDER_FACE, (x+1, y+1), (x+1,   y+h-2), 1)
    pygame.draw.line(surface, WIN_BORDER_MID,  (x+w-2, y+1), (x+w-2, y+h-2), 1)
    pygame.draw.line(surface, WIN_BORDER_MID,  (x+1, y+h-2), (x+w-2, y+h-2), 1)

    pygame.draw.line(surface, WIN_BORDER_LIGHT, (x+2, y+2), (x+w-3, y+2),   1)
    pygame.draw.line(surface, WIN_BORDER_LIGHT, (x+2, y+2), (x+2,   y+h-3), 1)
    pygame.draw.line(surface, WIN_BORDER_MID,   (x+w-3, y+2), (x+w-3, y+h-3), 1)
    pygame.draw.line(surface, WIN_BORDER_MID,   (x+2, y+h-3), (x+w-3, y+h-3), 1)


def _draw_titlebar_gradient(surface, x, y, w, h, focused=True):
    """WARN-04 FIX: Gradiente via Surface+scale — O(1) vs O(w) do loop original."""
    if not focused:
        pygame.draw.rect(surface, WIN_TITLE_INACTIVE, (x, y, w, h))
        return
    if w <= 0 or h <= 0:
        return
    c1, c2 = WIN_TITLE_ACTIVE1, WIN_TITLE_ACTIVE2
    # Cria gradiente de 2 pixels de largura e escala horizontalmente
    grad = pygame.Surface((2, max(h, 1)))
    grad.set_at((0, 0), c1)
    grad.set_at((1, 0), c2)
    # Preenche coluna de 2px na altura
    for row in range(1, max(h, 1)):
        grad.set_at((0, row), c1)
        grad.set_at((1, row), c2)
    # Escala para a largura real (muito mais rápido que loop pixel a pixel)
    scaled = pygame.transform.scale(grad, (max(w, 1), max(h, 1)))
    surface.blit(scaled, (x, y))


def _draw_system_icon(surface, x, y):
    sz = 14
    pygame.draw.rect(surface, (100, 160, 220), (x, y, sz, sz), border_radius=2)
    pygame.draw.rect(surface, (10,  36, 106),  (x, y, sz, 5))
    pygame.draw.rect(surface, (200, 220, 255), (x+1, y+6, sz-2, sz-7))
    pygame.draw.rect(surface, (10,  36, 106),  (x, y, sz, sz), 1, border_radius=2)


def _draw_win_btn(surface, rect, btn_type, focused=True):
    mx, my = pygame.mouse.get_pos()
    hover  = rect.collidepoint(mx, my)

    if btn_type == 'close' and hover:
        face = WIN_BTN_CLOSE_HOV
    elif hover:
        face = WIN_BTN_HOVER
    else:
        face = WIN_BTN_FACE

    pygame.draw.rect(surface, face, rect)
    bx, by, bw, bh = rect.x, rect.y, rect.width, rect.height

    if hover and btn_type == 'close':
        pygame.draw.line(surface, WIN_BORDER_DARK,  (bx,    by),    (bx+bw-1, by),    1)
        pygame.draw.line(surface, WIN_BORDER_DARK,  (bx,    by),    (bx,      by+bh-1), 1)
        pygame.draw.line(surface, WIN_BORDER_LIGHT, (bx+bw-1, by),  (bx+bw-1, by+bh-1), 1)
        pygame.draw.line(surface, WIN_BORDER_LIGHT, (bx, by+bh-1),  (bx+bw-1, by+bh-1), 1)
    else:
        pygame.draw.line(surface, WIN_BORDER_LIGHT, (bx,    by),    (bx+bw-1, by),    1)
        pygame.draw.line(surface, WIN_BORDER_LIGHT, (bx,    by),    (bx,      by+bh-1), 1)
        pygame.draw.line(surface, WIN_BORDER_DARK,  (bx+bw-1, by),  (bx+bw-1, by+bh-1), 1)
        pygame.draw.line(surface, WIN_BORDER_DARK,  (bx, by+bh-1),  (bx+bw-1, by+bh-1), 1)
        pygame.draw.line(surface, WIN_BORDER_MID,   (bx+bw-2, by+1), (bx+bw-2, by+bh-2), 1)
        pygame.draw.line(surface, WIN_BORDER_MID,   (bx+1, by+bh-2), (bx+bw-2, by+bh-2), 1)

    cx = rect.centerx; cy = rect.centery
    sc = (255,255,255) if (btn_type=='close' and hover) else (64,64,64)
    if btn_type == 'close_dis': sc = (160,160,160)

    if btn_type == 'min':
        pygame.draw.rect(surface, sc, (cx-4, cy+4, 8, 2))
    elif btn_type == 'max':
        pygame.draw.rect(surface, sc, (cx-4, cy-4, 9, 8), 1)
        pygame.draw.line(surface, sc, (cx-4, cy-4), (cx+4, cy-4), 2)
    elif btn_type == 'restore':
        pygame.draw.rect(surface, sc, (cx-2, cy-5, 7, 6), 1)
        pygame.draw.line(surface, sc, (cx-2, cy-5), (cx+4, cy-5), 2)
        pygame.draw.rect(surface, face, (cx-5, cy-2, 7, 6))
        pygame.draw.rect(surface, sc,   (cx-5, cy-2, 7, 6), 1)
        pygame.draw.line(surface, sc, (cx-5, cy-2), (cx+1, cy-2), 2)
    elif btn_type in ('close', 'close_dis'):
        pygame.draw.line(surface, sc, (cx-4, cy-4), (cx+4, cy+4), 2)
        pygame.draw.line(surface, sc, (cx+4, cy-4), (cx-4, cy+4), 2)
        pygame.draw.line(surface, sc, (cx-3, cy-4), (cx+4, cy+3), 2)
        pygame.draw.line(surface, sc, (cx+3, cy-4), (cx-4, cy+3), 2)


def _draw_resize_grip(surface, x, y):
    for i in range(3):
        for j in range(3-i):
            px = x + i*4 + j*4; py = y + j*4 + i*4
            pygame.draw.rect(surface, WIN_BORDER_LIGHT, (px+1, py+1, 2, 2))
            pygame.draw.rect(surface, WIN_BORDER_MID,   (px,   py,   2, 2))


# ── Compatibilidade ───────────────────────────────────────
def _dim(color, factor):
    return tuple(max(0, int(c*factor)) for c in color[:3])

def _draw_btn(surface, rect, color, symbol, font):
    _draw_win_btn(surface, rect,
                  'close' if symbol=='x' else
                  'min'   if symbol=='-' else 'max', True)


# ─────────────────────────────────────────────
#  HELPER GLOBAL — renderiza linhas numa janela COM SCROLL
# ─────────────────────────────────────────────
def draw_rows_in_win(surface, win, rows):
    """
    Renderiza lista de (texto, cor) dentro de win COM suporte a scroll.
    - Atualiza win._max_scroll baseado no conteúdo total
    - Usa win._scroll para offset vertical
    - A scrollbar é desenhada pelo draw_managed (fora do clip)
    """
    if not win.visible or win.minimized:
        return
    wfn  = win.font
    wlh  = win.line_height
    cr   = win.content_rect
    x0, y0, w0, h0 = cr.x, cr.y, cr.w, cr.h
    pad   = 8
    max_w = w0 - pad * 2

    total_content_h = len(rows) * wlh + pad * 2
    win._max_scroll  = max(0, total_content_h - h0)

    for i, (text, color) in enumerate(rows):
        ty = y0 + pad + i * wlh - win._scroll
        # Pular linhas fora da área visível
        if ty + wlh < y0:
            continue
        if ty > y0 + h0:
            break
        # Trunca texto largo
        rendered = text
        while rendered and wfn.size(rendered)[0] > max_w:
            rendered = rendered[:-1]
        if rendered != text:
            t = text
            while t and wfn.size(t + '…')[0] > max_w:
                t = t[:-1]
            rendered = t + ('…' if t != text else '')
        surface.blit(wfn.render(rendered, True, color), (x0 + pad, ty))
