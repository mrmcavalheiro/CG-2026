"""
============================================================
 exemplos/aula04/opengl_exemplos/_code_viewer.py
 Visualizador de código-fonte com syntax highlight,
 seleção de arquivo e scroll — usado pelos exemplos OpenGL.
============================================================
"""
import pygame
import config as cfg
from interface.tabs import TAB_H

SCROLL_SPD = 40
SB_W       = 10
PAD        = 12

# ── Paleta syntax highlight ──────────────────────────────
_KW   = (188, 140, 255)   # keywords
_BI   = (80,  180, 255)   # builtins/funcs
_STR  = (57,  213, 190)   # strings
_CMT  = (90,  150, 90)    # comments
_NUM  = (247, 129, 102)   # numbers
_OP   = (227, 179,  65)   # operators
_DEF  = (220, 235, 255)   # default

_KEYWORDS = {
    'def','class','return','if','elif','else','for','while','in',
    'not','and','or','True','False','None','import','from','as',
    'with','pass','break','continue','lambda','self','super',
}
_BUILTINS = {
    'print','len','range','int','float','str','list','dict','set',
    'glutInit','glutInitDisplayMode','glutInitWindowSize','glutCreateWindow',
    'glutDisplayFunc','glutIdleFunc','glutKeyboardFunc','glutSpecialFunc',
    'glutMainLoop','glutPostRedisplay','glutSwapBuffers','glutLeaveMainLoop',
    'glClear','glClearColor','glEnable','glMatrixMode','glLoadIdentity',
    'glTranslatef','glRotatef','glScalef','glPushMatrix','glPopMatrix',
    'glBegin','glEnd','glVertex2f','glVertex3f','glColor3f','glLineWidth',
    'glPointSize','glOrtho',
    'gluPerspective','gluLookAt','gluNewQuadric','gluQuadricDrawStyle',
    'gluSphere','gluDeleteQuadric',
}

import re as _re
_TOK = _re.compile(
    r'(""".*?"""|\'\'\'.*?\'\'\'|"[^"]*"|\'[^\']*\')'  # strings
    r'|(\b\d+\.?\d*\b)'                                  # numbers
    r'|([A-Za-z_]\w*)'                                   # identifiers
    r'|(#.*)'                                             # comments
    r'|(==|!=|<=|>=|[+\-*/=<>@|&])'                      # operators
    r'|(\S)',                                             # other
    _re.DOTALL
)


def _render_line(surface, line, x, y, font, max_w):
    if not line.strip():
        return
    # indentation
    stripped = line.lstrip()
    indent   = len(line) - len(stripped)
    cur_x    = x + font.size(' ')[0] * indent

    if stripped.startswith('#'):
        tw = font.size(line)[0]
        s  = font.render(line[:int(len(line)*max_w/max(tw,1))] if tw>max_w else line,
                         True, _CMT)
        surface.blit(s, (x, y))
        return

    for m in _TOK.finditer(stripped):
        tok = m.group(0)
        if   m.group(1): color = _STR
        elif m.group(2): color = _NUM
        elif m.group(3):
            if   tok in _KEYWORDS: color = _KW
            elif tok in _BUILTINS: color = _BI
            else:                  color = _DEF
        elif m.group(4): color = _CMT
        elif m.group(5): color = _OP
        else:            color = _DEF

        s = font.render(tok, True, color)
        if cur_x + s.get_width() > x + max_w:
            break
        surface.blit(s, (cur_x, y))
        cur_x += s.get_width() + (font.size(' ')[0] if tok != ' ' else 0)
        # handle spaces between tokens manually
        if m.end() < len(stripped) and stripped[m.end()] == ' ':
            cur_x += font.size(' ')[0]


class CodeViewer:
    """
    Renderiza código-fonte com syntax highlight, seleção de arquivo e scroll.
    arquivos: dict  nome -> list[str de linhas]
    """
    def __init__(self, arquivos: dict):
        self._files   = arquivos            # {nome: [linhas]}
        self._names   = list(arquivos.keys())
        self._active  = 0                   # índice do arquivo ativo
        self._scroll  = 0
        self._max_scroll = 0
        self._sb_dragging   = False
        self._sb_drag_start = 0
        self._dragging      = False
        self._drag_start    = 0
        self._tab_h     = TAB_H
        self._font_cache: dict = {}
        self._copy_flash = 0.0    # tempo de flash do botão Copiar

    def _font(self, size=12):
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.SysFont("monospace", size)
        return self._font_cache[size]

    def _canvas(self):
        cx, cy, cw, ch = cfg.canvas_rect()
        cy += self._tab_h; ch -= self._tab_h
        return cx, cy, cw, ch

    def _sb_thumb(self, cx, cy, cw, ch):
        track_h = ch - 36 - 8
        if self._max_scroll <= 0:
            return pygame.Rect(cx+cw-SB_W-4, cy+36+4, SB_W, track_h)
        ratio = track_h / max(track_h + self._max_scroll, 1)
        sb_h  = max(24, int(track_h * ratio))
        travel = track_h - sb_h
        sb_y   = cy + 36 + 4 + int(travel * self._scroll / max(self._max_scroll, 1))
        return pygame.Rect(cx+cw-SB_W-4, sb_y, SB_W, sb_h)

    def handle_scroll(self, dy):
        self._scroll = max(0, min(self._max_scroll, self._scroll - dy*SCROLL_SPD))

    def _copy_btn_rect(self, cx, cy, cw):
        """Rect do botão Copiar (canto direito da barra de abas)."""
        return pygame.Rect(cx + cw - 90, cy + 3, 84, 24)

    def _do_copy(self):
        """Copia o arquivo ativo para a área de transferência."""
        lines = self._files[self._names[self._active]]
        text  = '\n'.join(lines)
        try:
            pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode('utf-8'))
        except ImportError:
            pass   # pyperclip/scrap pode nao estar disponivel em todos os sistemas
        self._copy_flash = 1.2

    def handle_mouse_down(self, pos):
        cx, cy, cw, ch = self._canvas()
        # Botão Copiar
        if self._copy_btn_rect(cx, cy, cw).collidepoint(pos):
            self._do_copy()
            return True
        # Tab buttons at top (file selector)
        tab_w = max(80, cw // max(len(self._names), 1))
        for i, name in enumerate(self._names):
            r = pygame.Rect(cx + i*tab_w, cy, min(tab_w, cw-i*tab_w), 30)
            if r.collidepoint(pos):
                if i != self._active:
                    self._active = i
                    self._scroll = 0
                return True
        # Scrollbar
        sb_x = cx + cw - SB_W - 4
        if sb_x <= pos[0] <= sb_x+SB_W and cy+36 <= pos[1] <= cy+ch:
            self._sb_dragging   = True
            thumb = self._sb_thumb(cx, cy, cw, ch)
            self._sb_drag_start = pos[1] - thumb.y
            return True
        # Content drag
        if pygame.Rect(cx, cy+36, cw-SB_W-8, ch-36).collidepoint(pos):
            self._dragging   = True
            self._drag_start = pos[1] + self._scroll
            return True
        return False

    def handle_mouse_move(self, pos):
        if self._dragging:
            self._scroll = max(0, min(self._max_scroll, self._drag_start - pos[1]))
        if self._sb_dragging:
            cx, cy, cw, ch = self._canvas()
            thumb  = self._sb_thumb(cx, cy, cw, ch)
            travel = (ch - 36 - 8) - thumb.h
            if travel > 0:
                ratio = max(0.0, min(1.0, (pos[1]-self._sb_drag_start-(cy+36+4))/travel))
                self._scroll = int(ratio * self._max_scroll)

    def handle_mouse_up(self):
        self._dragging = self._sb_dragging = False

    def render(self, surface, fonts):
        cx, cy, cw, ch = self._canvas()
        pygame.draw.rect(surface, cfg.BG, (cx, cy, cw, ch))

        fn    = self._font(12)
        lh    = fn.get_height() + 3
        lines = self._files[self._names[self._active]]

        # ── File tab buttons ──────────────────────────
        tab_w = max(80, cw // max(len(self._names), 1))
        for i, name in enumerate(self._names):
            rx = cx + i * tab_w
            rw = min(tab_w, cw - i*tab_w)
            bg = cfg.TAB_ACTIVE if i == self._active else cfg.TAB_NORMAL
            pygame.draw.rect(surface, bg, (rx, cy, rw, 30))
            pygame.draw.rect(surface, cfg.BORDER, (rx, cy, rw, 30), 1)
            fn_t = fonts['sm']
            # Show short name
            short = name.split('/')[-1] if '/' in name else name
            t = fn_t.render(short, True, cfg.WHITE if i==self._active else cfg.GRAY)
            surface.blit(t, (rx+6, cy + 15 - t.get_height()//2))

        pygame.draw.line(surface, cfg.BORDER, (cx, cy+30), (cx+cw, cy+30))

        # ── Botão Copiar ──────────────────────────────
        cb = self._copy_btn_rect(cx, cy, cw)
        copied = self._copy_flash > 0
        cb_bg  = (30, 110, 50)  if copied else (30, 55, 30)
        cb_brd = (80, 220, 100) if copied else (60, 140, 60)
        cb_txt = '✓ Copiado!'   if copied else '⎘ Copiar'
        cb_cor = (100, 255, 130) if copied else (120, 200, 120)
        pygame.draw.rect(surface, cb_bg,  cb, border_radius=4)
        pygame.draw.rect(surface, cb_brd, cb, 1, border_radius=4)
        fn_cb = fonts['sm']
        t_cb  = fn_cb.render(cb_txt, True, cb_cor)
        surface.blit(t_cb, (cb.x + cb.w//2 - t_cb.get_width()//2,
                            cb.y + cb.h//2 - t_cb.get_height()//2))
        # Decai o flash por tempo (usando ticks)
        if self._copy_flash > 0:
            self._copy_flash -= 0.016   # ~1 frame a 60fps

        # ── Code area ─────────────────────────────────
        code_area = pygame.Rect(cx, cy+31, cw-SB_W-8, ch-31)
        old_clip = surface.get_clip()
        surface.set_clip(code_area)

        max_w = code_area.w - PAD*2
        total_h = len(lines) * lh + PAD*2
        self._max_scroll = max(0, total_h - code_area.h)
        self._scroll = max(0, min(self._scroll, self._max_scroll))

        y0 = cy + 31 + PAD - self._scroll
        for i, line in enumerate(lines):
            ty = y0 + i * lh
            if ty + lh < code_area.y: continue
            if ty > code_area.y + code_area.h: break
            # line number
            ln = fn.render(f"{i+1:3}", True, cfg.GRAY2)
            surface.blit(ln, (cx + PAD, ty))
            _render_line(surface, line.rstrip(), cx + PAD + 32, ty, fn, max_w - 32)

        surface.set_clip(old_clip)

        # ── Scrollbar ─────────────────────────────────
        track = pygame.Rect(cx+cw-SB_W-4, cy+36+4, SB_W, ch-36-8)
        pygame.draw.rect(surface, cfg.BG2, track, border_radius=4)
        pygame.draw.rect(surface, cfg.BORDER, track, 1, border_radius=4)
        if self._max_scroll > 0:
            thumb = self._sb_thumb(cx, cy, cw, ch)
            col = cfg.BLUE if self._sb_dragging else (70,130,200)
            pygame.draw.rect(surface, col, thumb, border_radius=4)
            pygame.draw.rect(surface, (150,200,255), thumb, 1, border_radius=4)
