"""
============================================================
 interface/doc_view.py
 Visualizador de documentos de teoria — dois modos:

   Modo PDF:     DocView("caminho/arquivo.pdf")
   Modo blocos:  DocView()  +  dv._blocks = DOCS["chave"]

 Helpers para criar blocos:
   _t _s _h _b _c _li _th _tr _eq _sep _bl
============================================================
"""

import os
import pygame
import config as cfg

# ─────────────────────────────────────────────
#  TIPOS DE BLOCO
# ─────────────────────────────────────────────
TITLE   = "title"
SUB     = "sub"
HEAD    = "head"
BODY    = "body"
CODE    = "code"
LIST    = "list"
TABLE_H = "table_h"
TABLE_R = "table_r"
EQ      = "eq"
SEP     = "sep"
BLANK   = "blank"

def _t(text):  return (TITLE,   text)
def _s(text):  return (SUB,     text)
def _h(text):  return (HEAD,    text)
def _b(text):  return (BODY,    text)
def _c(text):  return (CODE,    text)
def _li(text): return (LIST,    text)
def _th(text): return (TABLE_H, text)
def _tr(text): return (TABLE_R, text)
def _eq(text): return (EQ,      text)
def _sep():    return (SEP,     "")
def _bl():     return (BLANK,   "")

DOCS: dict = {}

_PAD      = 18
_LINE_GAP = 4
_CODE_PAD = 8
_SB_W     = 12

_font_cache: dict = {}

def _font(name, size, bold=False):
    key = (name, size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size, bold=bold)
    return _font_cache[key]

def _fn_title():  return _font("segoeui",  20, True)
def _fn_sub():    return _font("segoeui",  15, True)
def _fn_head():   return _font("segoeui",  13, True)
def _fn_body():   return _font("segoeui",  13)
def _fn_code():   return _font("monospace",12)
def _fn_eq():     return _font("segoeui",  13, True)

def _wrap(text, font, max_w):
    if not text.strip():
        return [""]
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


_BTN_H = 28
_BTN_W = 110

class DocView:
    def __init__(self, pdf_path="", fallback_blocks=None, download_pdf=""):
        self._pdf_path    = pdf_path
        self._download    = download_pdf   # caminho para abrir/baixar PDF
        self._blocks      = []
        self._fallback    = fallback_blocks or []
        self._loaded      = False
        self._pdf_pages   = []
        self._mode        = "blocks" if not pdf_path else "pdf"
        self._scroll      = 0
        self._max_scroll  = 0
        self._tab_off     = 0
        self._sb_drag     = False
        self._sb_drag_y   = 0
        self._btn_hover   = False
        self._key         = ""
        if pdf_path:
            self._try_load_pdf()
        elif self._fallback:
            self._blocks = self._fallback
            self._loaded = True

    def set_tab_offset(self, h):
        self._tab_off = h

    def _try_load_pdf(self):
        try:
            import fitz
            doc = fitz.open(self._pdf_path)
            self._pdf_pages = []
            for page in doc:
                mat = fitz.Matrix(1.5, 1.5)
                pix = page.get_pixmap(matrix=mat)
                img = pygame.image.frombytes(pix.samples, (pix.width, pix.height), "RGB")
                self._pdf_pages.append(img)
            self._loaded = True
            self._mode   = "pdf"
        except ImportError:
            self._mode   = "blocks"
            self._loaded = True
            if self._fallback:
                self._blocks = self._fallback
            else:
                fname = self._pdf_path.replace("\\", "/").split("/")[-1]
                self._blocks = [
                    _t(f"PDF: {fname}"),
                    _sep(),
                    _b("Para visualizar o PDF instale o pymupdf:"),
                    _c("pip install pymupdf"),
                    _bl(),
                    _b("O conteúdo da teoria está no arquivo PDF na pasta 'teoria/'."),
                ]
        except Exception as e:
            self._mode   = "blocks"
            self._loaded = True
            if self._fallback:
                self._blocks = self._fallback
            else:
                self._blocks = [
                    _t("Erro ao carregar PDF"),
                    _sep(),
                    _b(str(e)),
                ]

    def _clamp_scroll(self):
        self._scroll = max(0, min(self._max_scroll, self._scroll))

    def _btn_rect(self):
        """Retorna Rect do botão 'Abrir PDF', ou None se não houver download_pdf."""
        if not self._download:
            return None
        cx, cy, cw, ch = cfg.canvas_rect()
        bx = cx + cw - _SB_W - _BTN_W - 8
        by = cy + self._tab_off + 6
        return pygame.Rect(bx, by, _BTN_W, _BTN_H)

    def _open_pdf(self):
        path = self._download
        if not os.path.isfile(path):
            return
        try:
            if os.name == "nt":
                os.startfile(path)  # Windows
            else:
                import subprocess
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

    def handle_scroll(self, dy):
        self._scroll -= dy * 40
        self._clamp_scroll()

    def handle_mouse_down(self, pos, canvas_rect=None):
        btn = self._btn_rect()
        if btn and btn.collidepoint(pos):
            self._open_pdf()
            return True
        sb = self._sb_rect()
        if sb and sb.collidepoint(pos):
            self._sb_drag   = True
            self._sb_drag_y = pos[1]
            return True
        return False

    def handle_mouse_move(self, pos):
        btn = self._btn_rect()
        self._btn_hover = bool(btn and btn.collidepoint(pos))
        if self._sb_drag:
            dy = pos[1] - self._sb_drag_y
            self._sb_drag_y = pos[1]
            if self._max_scroll > 0:
                h = self._content_rect()[3]
                self._scroll += int(dy * self._max_scroll / max(h, 1))
                self._clamp_scroll()

    def handle_mouse_up(self):
        self._sb_drag = False

    def _content_rect(self):
        cx, cy, cw, ch = cfg.canvas_rect()
        y = cy + self._tab_off
        h = ch - self._tab_off
        return (cx, y, cw - _SB_W - 2, h)

    def _sb_rect(self):
        cx, cy, cw, ch = cfg.canvas_rect()
        y = cy + self._tab_off
        h = ch - self._tab_off
        if h <= 0:
            return None
        return pygame.Rect(cx + cw - _SB_W - 1, y, _SB_W, h)

    def _sb_thumb_rect(self):
        sb = self._sb_rect()
        if not sb or self._max_scroll <= 0:
            return sb
        content_h = sb.h + self._max_scroll
        ratio   = sb.h / max(content_h, 1)
        thumb_h = max(24, int(sb.h * ratio))
        travel  = sb.h - thumb_h
        thumb_y = sb.y + int(travel * self._scroll / max(self._max_scroll, 1))
        return pygame.Rect(sb.x, thumb_y, sb.w, thumb_h)

    def render(self, surface):
        if not self._loaded:
            return
        if self._mode == "pdf":
            self._render_pdf(surface)
        else:
            self._render_blocks(surface)
        self._draw_scrollbar(surface)
        self._draw_btn(surface)

    def _render_pdf(self, surface):
        if not self._pdf_pages:
            return
        cx, cy, cw, ch = cfg.canvas_rect()
        y0 = cy + self._tab_off
        h0 = ch - self._tab_off
        pygame.draw.rect(surface, cfg.BG2, (cx, y0, cw, h0))
        total_h = sum(int(p.get_height() * (cw - _SB_W - 4) / max(p.get_width(), 1)) + 8
                      for p in self._pdf_pages)
        self._max_scroll = max(0, total_h - h0)
        self._clamp_scroll()
        old_clip = surface.get_clip()
        surface.set_clip(pygame.Rect(cx, y0, cw - _SB_W - 2, h0))
        y = y0 - self._scroll
        for page in self._pdf_pages:
            pw = page.get_width()
            ph = page.get_height()
            scale = (cw - _SB_W - 4) / max(pw, 1)
            new_w = int(pw * scale)
            new_h = int(ph * scale)
            if y + new_h > y0 and y < y0 + h0:
                scaled = pygame.transform.smoothscale(page, (new_w, new_h))
                surface.blit(scaled, (cx, y))
            y += new_h + 8
        surface.set_clip(old_clip)

    def _render_blocks(self, surface):
        cr = self._content_rect()
        x0, y0, w0, h0 = cr
        pygame.draw.rect(surface, cfg.BG, (x0, y0, w0 + _SB_W + 2, h0))
        inner_w = w0 - _PAD * 2
        total_h = _PAD + sum(self._block_height(bt, bx, inner_w)
                             for bt, bx in self._blocks) + _PAD
        self._max_scroll = max(0, total_h - h0)
        self._clamp_scroll()
        old_clip = surface.get_clip()
        surface.set_clip(pygame.Rect(x0, y0, w0, h0))
        y = y0 + _PAD - self._scroll
        for btype, btext in self._blocks:
            y = self._draw_block(surface, btype, btext, x0 + _PAD, y, inner_w)
            if y > y0 + h0 + 300:
                break
        surface.set_clip(old_clip)

    def _block_height(self, btype, btext, w):
        if btype == BLANK:   return 10
        if btype == SEP:     return 14
        if btype == TITLE:   return _fn_title().get_height() + 10
        if btype == SUB:     return _fn_sub().get_height() + 8
        if btype == HEAD:    return _fn_head().get_height() + 16
        if btype == CODE:    return _fn_code().get_height() + _CODE_PAD + 2
        if btype in (TABLE_H, TABLE_R): return _fn_body().get_height() + 8
        if btype == EQ:      return _fn_eq().get_height() + 22
        fn   = _fn_body()
        text = ("• " + btext) if btype == LIST else btext
        return len(_wrap(text, fn, w)) * (_fn_body().get_height() + _LINE_GAP) + 6

    def _draw_block(self, surface, btype, btext, x, y, w):
        if btype == BLANK:
            return y + 10
        if btype == SEP:
            pygame.draw.line(surface, cfg.BORDER, (x, y+6), (x+w, y+6), 1)
            return y + 14
        if btype == TITLE:
            fn = _fn_title()
            s  = fn.render(btext, True, cfg.WHITE)
            surface.blit(s, (x, y))
            pygame.draw.line(surface, cfg.BLUE,
                             (x, y+fn.get_height()+2), (x+w, y+fn.get_height()+2), 2)
            return y + fn.get_height() + 10
        if btype == SUB:
            fn = _fn_sub()
            s  = fn.render(btext, True, cfg.CYAN)
            surface.blit(s, (x, y))
            return y + fn.get_height() + 8
        if btype == HEAD:
            fn  = _fn_head()
            bgh = fn.get_height() + 6
            pygame.draw.rect(surface, cfg.BG3, (x-4, y, w+8, bgh), border_radius=3)
            pygame.draw.rect(surface, cfg.BLUE, (x-4, y, 4, bgh), border_radius=2)
            s = fn.render(btext, True, cfg.BLUE)
            surface.blit(s, (x+4, y+3))
            return y + bgh + 10
        if btype == CODE:
            fn  = _fn_code()
            lh  = fn.get_height() + _CODE_PAD
            pygame.draw.rect(surface, cfg.BG2, (x, y, w, lh), border_radius=3)
            pygame.draw.rect(surface, cfg.BORDER, (x, y, w, lh), 1, border_radius=3)
            pygame.draw.rect(surface, cfg.GREEN, (x, y, 3, lh), border_radius=2)
            code_text = btext
            max_w = w - _CODE_PAD * 2 - 6
            while code_text and fn.size(code_text)[0] > max_w:
                code_text = code_text[:-1]
            if code_text != btext:
                code_text = code_text[:-1] + "…"
            s = fn.render(code_text, True, cfg.GREEN)
            surface.blit(s, (x + _CODE_PAD + 2, y + _CODE_PAD // 2))
            return y + lh + 2
        if btype in (TABLE_H, TABLE_R):
            fn    = _fn_body()
            lh    = fn.get_height() + 8
            cols  = [c.strip() for c in btext.split("|")]
            col_w = w // max(len(cols), 1)
            bg    = cfg.BG3 if btype == TABLE_H else cfg.BG2
            tc    = cfg.CYAN if btype == TABLE_H else cfg.WHITE
            pygame.draw.rect(surface, bg, (x, y, w, lh))
            pygame.draw.rect(surface, cfg.BORDER, (x, y, w, lh), 1)
            for ci, col in enumerate(cols):
                s = fn.render(col, True, tc)
                surface.blit(s, (x + ci*col_w + 4, y+4))
            return y + lh
        if btype == EQ:
            fn  = _fn_eq()
            bgh = fn.get_height() + 10
            pygame.draw.rect(surface, cfg.BG2, (x, y, w, bgh), border_radius=4)
            pygame.draw.rect(surface, cfg.PURPLE, (x, y, w, bgh), 1, border_radius=4)
            s = fn.render(btext, True, cfg.PURPLE)
            surface.blit(s, (x + w//2 - s.get_width()//2, y+5))
            return y + bgh + 12
        # BODY / LIST
        fn    = _fn_body()
        text  = ("• " + btext) if btype == LIST else btext
        tc    = cfg.WHITE if btype == BODY else cfg.GRAY
        lines = _wrap(text, fn, w)
        lh    = fn.get_height() + _LINE_GAP
        for line in lines:
            s = fn.render(line, True, tc)
            surface.blit(s, (x, y))
            y += lh
        return y + 6

    def _draw_btn(self, surface):
        btn = self._btn_rect()
        if not btn:
            return
        exists = os.path.isfile(self._download)
        bg  = (50, 90, 140) if (self._btn_hover and exists) else (30, 55, 90)
        fc  = cfg.WHITE if exists else cfg.GRAY2
        pygame.draw.rect(surface, bg, btn, border_radius=5)
        pygame.draw.rect(surface, cfg.BLUE, btn, 1, border_radius=5)
        fn = _font("segoeui", 12)
        label = "Abrir PDF" if exists else "PDF indisponível"
        s = fn.render(label, True, fc)
        surface.blit(s, (btn.x + (btn.w - s.get_width())//2,
                          btn.y + (btn.h - s.get_height())//2))

    def _draw_scrollbar(self, surface):
        sb = self._sb_rect()
        if not sb:
            return
        pygame.draw.rect(surface, cfg.BG3, sb, border_radius=4)
        pygame.draw.rect(surface, cfg.BORDER, sb, 1, border_radius=4)
        if self._max_scroll > 0:
            thumb = self._sb_thumb_rect()
            col   = cfg.BLUE if self._sb_drag else (80, 130, 200)
            pygame.draw.rect(surface, col, thumb, border_radius=4)
            pygame.draw.rect(surface, (150, 200, 255), thumb, 1, border_radius=4)
