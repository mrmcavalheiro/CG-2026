"""
============================================================
 exemplos/aula05/clipping.py

 Exemplo interativo: Recorte (Clipping) — Cohen-Sutherland

 Demonstra:
  - Janela de recorte (retangulo laranja)
  - Segmentos de reta sendo classificados:
      VERDE   = totalmente visivel (aceito)
      AMARELO = parcialmente visivel (recortado)
      VERMELHO = totalmente fora (rejeitado)
  - Codigos de 4 bits exibidos para cada extremidade
  - Algoritmo passo a passo visivel

 Controles:
  - ESPACO:   gerar novos segmentos aleatorios
  - Setas:    mover a janela de recorte
  - W/S/A/D:  redimensionar a janela
  - R:        resetar
============================================================
"""

import pygame
import math
import random
import config as cfg
from exemplos.base import ExemploBase
from interface.ui  import draw_label, draw_line_alpha
from interface.tabs   import TabBar, TAB_H
from interface.doc_view import DocView
from interface.janela import WindowManager, draw_rows_in_win


def cohen_code(x, y, xmin, xmax, ymin, ymax):
    """Retorna codigo de 4 bits de Cohen-Sutherland."""
    code = 0
    if y > ymax: code |= 8   # TOPO
    if y < ymin: code |= 4   # BASE
    if x > xmax: code |= 2   # DIREITA
    if x < xmin: code |= 1   # ESQUERDA
    return code


def cohen_sutherland(x1, y1, x2, y2, xmin, xmax, ymin, ymax):
    """
    Algoritmo de Cohen-Sutherland.
    Retorna (aceito, recortado, x1c, y1c, x2c, y2c)
    """
    c1 = cohen_code(x1, y1, xmin, xmax, ymin, ymax)
    c2 = cohen_code(x2, y2, xmin, xmax, ymin, ymax)

    for _ in range(10):
        if c1 == 0 and c2 == 0:
            return True, True, x1, y1, x2, y2   # aceitar
        if c1 & c2 != 0:
            return False, False, x1, y1, x2, y2  # rejeitar
        # escolhe ponto fora
        cout = c1 if c1 != 0 else c2
        if cout & 8:   # TOPO
            xi = x1 + (x2-x1)*(ymax-y1)/(y2-y1) if y2!=y1 else x1
            yi = ymax
        elif cout & 4:  # BASE
            xi = x1 + (x2-x1)*(ymin-y1)/(y2-y1) if y2!=y1 else x1
            yi = ymin
        elif cout & 2:  # DIREITA
            yi = y1 + (y2-y1)*(xmax-x1)/(x2-x1) if x2!=x1 else y1
            xi = xmax
        else:           # ESQUERDA
            yi = y1 + (y2-y1)*(xmin-x1)/(x2-x1) if x2!=x1 else y1
            xi = xmin
        if cout == c1:
            x1, y1, c1 = xi, yi, cohen_code(xi, yi, xmin, xmax, ymin, ymax)
        else:
            x2, y2, c2 = xi, yi, cohen_code(xi, yi, xmin, xmax, ymin, ymax)

    return False, False, x1, y1, x2, y2



class ExClipping(ExemploBase):
    NAME  = "Clipping"
    COLOR = cfg.RED

    # Tamanho do espaco de trabalho em pixels do canvas
    AREA = 300

    def __init__(self):
        super().__init__()
        # Janela de recorte (coords 0..AREA)
        self.win_x  = 80
        self.win_y  = 60
        self.win_w  = 140
        self.win_h  = 120
        self.segs   = []
        self.flash  = 0.0
        self._mgr   = None
        self._teoria   = DocView(cfg.root_path("teoria", "Aula_05", "clipping.pdf"))
        self._teoria.set_tab_offset(TAB_H)
        self._tabs  = TabBar(["Demonstração", "Teoria"])
        self._gen_segments()

    def _gen_segments(self):
        """Gera segmentos aleatorios para demonstracao."""
        random.seed(42)
        self.segs = []
        A = self.AREA
        for _ in range(8):
            x1 = random.randint(5, A-5)
            y1 = random.randint(5, A-5)
            x2 = random.randint(5, A-5)
            y2 = random.randint(5, A-5)
            self.segs.append((x1, y1, x2, y2))


    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Clipping — Cohen-Sutherland",
            cax+10, cay+10, 265, 430, color=(180,30,30), closable=False)
        self._win_code = self._mgr.create("Cohen-Sutherland",
            cax+10, cay+455, 265, 200, color=(60,40,120), closable=False)
        self._tabs.bind_mgr(self._mgr)


    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 0 and self._mgr:
            if self._mgr.handle_mouse_down(pos): return True
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._mgr: self._mgr.handle_mouse_move(pos)

    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)

    def handle_scroll(self, dy):
        if self._tabs.active == 1:
            self._teoria.handle_scroll(dy)
        elif self._mgr:
            self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)
        else:
            self._tabs.handle_scroll(dy)

    def reset(self):
        self.win_x = 80;  self.win_y = 60
        self.win_w = 140; self.win_h = 120
        self._gen_segments()
        self.flash = 0.0

    def toggle_anim(self):
        """Gera novos segmentos aleatorios.
        WARN-05 FIX: Usa time-based seed em vez de randint sem seed proprio.
        """
        import time
        random.seed(int(time.time() * 1000) % 100000)
        A = self.AREA
        self.segs = []
        for _ in range(8):
            x1 = random.randint(5, A-5)
            y1 = random.randint(5, A-5)
            x2 = random.randint(5, A-5)
            y2 = random.randint(5, A-5)
            self.segs.append((x1, y1, x2, y2))

    def handle_action(self, action):
        step = 8
        if   action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':       self.reset()
        elif action == 'inc':         self.win_y = max(5, self.win_y - step);  self.flash=0.3
        elif action == 'dec':         self.win_y = min(self.AREA-self.win_h-5, self.win_y+step); self.flash=0.3
        elif action == 'inc_alt':     self.win_x = min(self.AREA-self.win_w-5, self.win_x+step); self.flash=0.3
        elif action == 'dec_alt':     self.win_x = max(5, self.win_x - step);  self.flash=0.3

    def handle_extra(self, key):
        step = 8
        if   key == pygame.K_w: self.win_h = max(30, self.win_h - step);  self.flash=0.3
        elif key == pygame.K_s: self.win_h = min(self.AREA-self.win_y-5, self.win_h+step); self.flash=0.3
        elif key == pygame.K_a: self.win_w = max(30, self.win_w - step);  self.flash=0.3
        elif key == pygame.K_d: self.win_w = min(self.AREA-self.win_x-5, self.win_w+step); self.flash=0.3

    def update(self, dt):
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)

    def draw(self, surface, fonts):
        cr  = cfg.canvas_rect()
        cax, cay, caw, cah = cr

        # Fundo já pintado pelo _draw() principal

        # Ajusta área de conteúdo abaixo das abas
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cax = drx; cay = dry
        caw = drw; cah = drh

        fn = fonts['sm']

        # ── Posicionar area de trabalho ──────────────────
        A   = self.AREA
        off_x = cax + 200   # deixa espaco para info box
        off_y = cay + (cah - A) // 2
        off_y = max(cay + 15, off_y)

        # xmin/xmax/ymin/ymax da janela (coords absolutas)
        wxmin = off_x + self.win_x
        wxmax = off_x + self.win_x + self.win_w
        wymin = off_y + self.win_y               # TOPO (y cresce para baixo)
        wymax = off_y + self.win_y + self.win_h  # BASE

        # ── Fundo da area de trabalho ─────────────────────
        pygame.draw.rect(surface, cfg.BG2,
                         (off_x, off_y, A, A))
        pygame.draw.rect(surface, cfg.BORDER,
                         (off_x, off_y, A, A), 1)

        # grid
        for g in range(0, A+1, 50):
            pygame.draw.line(surface, cfg.GRAY2,
                             (off_x+g, off_y), (off_x+g, off_y+A), 1)
            pygame.draw.line(surface, cfg.GRAY2,
                             (off_x, off_y+g), (off_x+A, off_y+g), 1)

        # ── 9 regioes de Cohen-Sutherland ─────────────────
        region_colors = {
            (0,0):(0,30,0), (1,0):(20,0,0), (-1,0):(20,0,0),
            (0,1):(20,0,0), (0,-1):(20,0,0),
            (1,1):(15,0,0), (-1,1):(15,0,0),
            (1,-1):(15,0,0),(-1,-1):(15,0,0),
        }

        region_codes = [
            ("1001","1000","1010"),
            ("0001","0000","0010"),
            ("0101","0100","0110"),
        ]

        # labels de codigos nas regioes
        for ri, row in enumerate(region_codes):
            for ci, code in enumerate(row):
                if ri == 0: ry = off_y + 2
                elif ri == 1: ry = wymin + (wymax-wymin)//2 - 8
                else: ry = wymax + 4

                if ci == 0: rx = off_x + 2
                elif ci == 1: rx = wxmin + (wxmax-wxmin)//2 - 16
                else: rx = wxmax + 4

                is_inside = (code == "0000")
                c = cfg.GREEN if is_inside else cfg.GRAY2
                s = fn.render(code, True, c)
                surface.blit(s, (rx, ry))

        # ── Janela de recorte ─────────────────────────────
        # preenchimento semi-transparente
        surf_win = pygame.Surface((self.win_w, self.win_h), pygame.SRCALPHA)
        surf_win.fill((*cfg.GREEN, 18))
        surface.blit(surf_win, (wxmin, wymin))

        wc = cfg.YELLOW if self.flash > 0 else cfg.GREEN
        pygame.draw.rect(surface, wc,
                         (wxmin, wymin, self.win_w, self.win_h), 2)
        draw_label(surface, "Janela", wxmin+3, wymin+2, fn, wc, cfg.BG2)

        # ── Segmentos de reta ─────────────────────────────
        stats = {'aceitos':0, 'recortados':0, 'rejeitados':0}
        details = []

        for x1, y1, x2, y2 in self.segs:
            ax1 = off_x + x1; ay1 = off_y + y1
            ax2 = off_x + x2; ay2 = off_y + y2

            # coordenadas relativas a janela (para Cohen)
            c1 = cohen_code(x1, y1,
                            self.win_x, self.win_x+self.win_w,
                            self.win_y, self.win_y+self.win_h)
            c2 = cohen_code(x2, y2,
                            self.win_x, self.win_x+self.win_w,
                            self.win_y, self.win_y+self.win_h)

            aceito, recortado, rx1, ry1, rx2, ry2 = cohen_sutherland(
                x1, y1, x2, y2,
                self.win_x, self.win_x+self.win_w,
                self.win_y, self.win_y+self.win_h
            )

            if not aceito:
                # BUG-03 FIX: not aceito = totalmente fora (rejeitar)
                pygame.draw.line(surface, cfg.RED,
                                 (ax1,ay1), (ax2,ay2), 1)
                stats['rejeitados'] += 1
                status = "REJEITAR"
                color  = cfg.RED
            elif rx1!=x1 or ry1!=y1 or rx2!=x2 or ry2!=y2:
                # aceito com recorte = parcialmente visível
                draw_line_alpha(surface, cfg.GRAY2, (ax1,ay1), (ax2,ay2), 1, alpha=80)
                # parte recortada em amarelo
                pygame.draw.line(surface, cfg.YELLOW,
                                 (int(off_x+rx1), int(off_y+ry1)),
                                 (int(off_x+rx2), int(off_y+ry2)), 2)
                # pontos de intersecao
                pygame.draw.circle(surface, cfg.WHITE,
                                   (int(off_x+rx1), int(off_y+ry1)), 4)
                pygame.draw.circle(surface, cfg.WHITE,
                                   (int(off_x+rx2), int(off_y+ry2)), 4)
                stats['recortados'] += 1
                status = "RECORTAR"
                color  = cfg.YELLOW
            else:
                # aceito sem recorte = totalmente dentro
                pygame.draw.line(surface, cfg.GREEN,
                                 (ax1,ay1), (ax2,ay2), 2)
                stats['aceitos'] += 1
                status = "ACEITAR"
                color  = cfg.GREEN

            # codigos nas extremidades
            s = fn.render(f"{c1:04b}", True, (*color, 180))
            surface.blit(s, (ax1-18, ay1-12))
            s = fn.render(f"{c2:04b}", True, (*color, 180))
            surface.blit(s, (ax2+4, ay2-12))

            details.append((status, c1, c2, color))

        # ── Legenda ────────────────────────────────────────
        legends = [
            (cfg.GREEN,  f"Aceito:     {stats['aceitos']}"),
            (cfg.YELLOW, f"Recortado:  {stats['recortados']}"),
            (cfg.RED,    f"Rejeitado:  {stats['rejeitados']}"),
        ]
        for li, (lc, lt) in enumerate(legends):
            pygame.draw.line(surface, lc,
                             (off_x+A+10, off_y+10+li*18),
                             (off_x+A+30, off_y+10+li*18), 3)
            s = fn.render(lt, True, lc)
            surface.blit(s, (off_x+A+34, off_y+3+li*18))

        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        rows_info = [
            ("Clipping",               cfg.RED),
            ("Cohen-Sutherland",       cfg.ORANGE),
            ("",                       cfg.WHITE),
            ("Codigos 4 bits:",        cfg.CYAN),
            (" bit3=TOPO  bit2=BASE",  cfg.GRAY),
            (" bit1=DIR   bit0=ESQ",   cfg.GRAY),
            ("",                       cfg.WHITE),
            ("Regras:",                cfg.ORANGE),
            (" 0000+0000 -> ACEITAR",  cfg.GREEN),
            (" AND!=0  -> REJEITAR",   cfg.RED),
            (" Senao   -> RECORTAR",   cfg.YELLOW),
            ("",                       cfg.WHITE),
            (f"Aceitos:    {stats['aceitos']}", cfg.GREEN),
            (f"Recortados: {stats['recortados']}", cfg.YELLOW),
            (f"Rejeitados: {stats['rejeitados']}", cfg.RED),
            ("",                       cfg.WHITE),
            ("[ESP] Novos segmentos",   cfg.YELLOW),
            ("[Setas] Mover janela",    cfg.YELLOW),
            ("[W/S/A/D] Redimensionar", cfg.YELLOW),
        ]
        rows_code = [
            ("def code(x,y,xn,xx,yn,yx):", cfg.WHITE),
            ("  c = 0",                (100,140,100)),
            ("  if y > yx: c |= 8",   cfg.WHITE),
            ("  if y < yn: c |= 4",   cfg.WHITE),
            ("  if x > xx: c |= 2",   cfg.WHITE),
            ("  if x < xn: c |= 1",   cfg.WHITE),
            ("  return c",             cfg.WHITE),
            ("",                       cfg.WHITE),
            ("c1 = code(x1,y1,...)",   cfg.WHITE),
            ("c2 = code(x2,y2,...)",   cfg.WHITE),
            ("if c1==0 and c2==0:",    (188,140,255)),
            ("  # ACEITAR",            (100,140,100)),
            ("elif c1 & c2 != 0:",     (188,140,255)),
            ("  # REJEITAR",           (100,140,100)),
        ]
        def _content(win, surf):
            if   win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_code: draw_rows_in_win(surf, win, rows_code)
        self._mgr.draw_managed(surface, fonts, _content)


