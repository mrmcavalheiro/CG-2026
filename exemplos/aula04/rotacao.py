"""
============================================================
 exemplos/rotacao.py
 Rotacao 2D — com botoes CCW/CW na demonstracao
============================================================
"""
import math
import numpy as np
import pygame
import config as cfg
from exemplos.base      import ExemploBase
from exemplos.docs_teoria import DOCS_TEORIA
from interface.janela   import WindowManager, draw_rows_in_win
from interface.ui       import draw_grid, draw_axes, world_to_screen, draw_polygon
from interface.tabs     import TabBar, TAB_H
from interface.doc_view import DocView

CCW = +1
CW  = -1

# Forma base: letra "F" para evidenciar rotacao
SHAPE = np.array([
    [-40, -50], [ 40, -50], [ 40, -30], [  0, -30],
    [  0, -10], [ 30, -10], [ 30,  10], [  0,  10],
    [  0,  50], [-40,  50],
], dtype=float)


class ExRotacao(ExemploBase):
    NAME  = "Rotação"
    COLOR = cfg.PURPLE
    SPEED = 45.0

    def __init__(self):
        super().__init__()
        self.angle     = 0.0
        self.direction = CCW
        self.running   = True
        self.flash     = 0.0
        self._mgr      = None
        self._tabs     = TabBar(["Demonstração", "Teoria"])
        self._teoria   = DocView(fallback_blocks=DOCS_TEORIA["rotacao"],
                               download_pdf=cfg.root_path("teoria","Aula_04","rotacao.pdf"))
        self._win_info = None
        self._win_code = None
        self._btn_ccw  = None   # Rect do botão CCW
        self._btn_cw   = None   # Rect do botão CW

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Rotação 2D",
            cax+10, cay+10, 265, 310, color=(80,30,160), closable=False)
        self._win_code = self._mgr.create("Python — NumPy",
            cax+10, cay+335, 265, 240, color=(60,40,120), closable=False)
        self._tabs.bind_mgr(self._mgr)

    def reset(self):
        self.angle   = 0.0
        self.running = True
        self.flash   = 0.0

    def toggle_anim(self): self.running = not self.running

    def set_direction(self, d):
        if self.direction != d:
            self.direction = d
            self.flash = 0.4

    def handle_action(self, action):
        if   action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':       self.reset()
        elif action == 'inc':         self.angle = (self.angle + 5) % 360
        elif action == 'dec':         self.angle = (self.angle - 5 + 360) % 360
        elif action == 'toggle_dir':  self.set_direction(-self.direction)

    def handle_extra(self, key):
        if key == pygame.K_d: self.set_direction(-self.direction)

    def handle_mouse_down(self, pos):
        # Botões CCW / CW
        if self._btn_ccw and pygame.Rect(*self._btn_ccw).collidepoint(pos):
            self.set_direction(CCW); return True
        if self._btn_cw  and pygame.Rect(*self._btn_cw).collidepoint(pos):
            self.set_direction(CW);  return True

        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 1:
            return self._teoria.handle_mouse_down(pos, cfg.canvas_rect())
        if self._tabs.active == 0 and self._mgr:
            return self._mgr.handle_mouse_down(pos)
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 1:
            self._teoria.handle_mouse_move(pos)
        elif self._mgr:
            self._mgr.handle_mouse_move(pos)

    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        self._teoria.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)

    def handle_scroll(self, dy):
        if self._tabs.active == 1:
            self._teoria.handle_scroll(dy)
        elif self._mgr:
            self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)

    def update(self, dt):
        if self.running:
            # Ângulo sempre cresce — a direção é aplicada na matriz de rotação
            self.angle = (self.angle + self.SPEED * dt) % 360
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)

    def draw(self, surface, fonts):
        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        # Teoria: PDF
        if self._tabs.active == 1:
            self._teoria.render(surface)
            return

        cr = cfg.canvas_rect()
        cax, cay, caw, cah = cr
        cay = cay + TAB_H
        cah = cah - TAB_H
        cr  = (cax, cay, caw, cah)
        cx  = caw // 2
        cy  = cah // 2

        draw_grid(surface, cr, cx, cy)
        draw_axes(surface, cr, cx, cy, font=fonts['sm'])

        # Botões CCW / CW no canvas (topo direito)
        fn_btn = fonts['tab']
        btn_w, btn_h = 130, 34
        btn_gap = 8
        btn_y   = cay + 14
        btn_x1  = cax + caw - (btn_w * 2 + btn_gap + 12)
        btn_x2  = btn_x1 + btn_w + btn_gap

        self._btn_ccw = (btn_x1, btn_y, btn_w, btn_h)
        self._btn_cw  = (btn_x2, btn_y, btn_w, btn_h)

        mx, my = pygame.mouse.get_pos()

        for rect, label, is_dir in [
            (self._btn_ccw, "↺  Anti-Horário", self.direction == CCW),
            (self._btn_cw,  "↻  Horário",      self.direction == CW),
        ]:
            rx, ry, rw, rh = rect
            r = pygame.Rect(rx, ry, rw, rh)

            if is_dir:
                bg  = cfg.BLUE if self.direction == CCW else cfg.ORANGE
                tc  = cfg.WHITE
                brd = cfg.WHITE
            elif r.collidepoint(mx, my):
                bg  = cfg.TAB_HOVER
                tc  = cfg.WHITE
                brd = cfg.GRAY2
            else:
                bg  = cfg.BG2
                tc  = cfg.GRAY
                brd = cfg.BORDER

            pygame.draw.rect(surface, bg,  r, border_radius=6)
            pygame.draw.rect(surface, brd, r, 2, border_radius=6)
            txt = fn_btn.render(label, True, tc)
            surface.blit(txt, txt.get_rect(center=r.center))

        # Indicador circular animado
        ox = cax + cx
        oy = cay + cy
        arc_r   = 60
        arc_col = cfg.BLUE if self.direction == CCW else cfg.ORANGE

        # Arco de progresso do ângulo
        ang_rad = math.radians(self.angle)
        try:
            if self.direction == CCW:
                pygame.draw.arc(surface, arc_col,
                    (ox-arc_r, oy-arc_r, arc_r*2, arc_r*2),
                    0, ang_rad + 0.01, 3)
            else:
                pygame.draw.arc(surface, arc_col,
                    (ox-arc_r, oy-arc_r, arc_r*2, arc_r*2),
                    -ang_rad, 0.01, 3)
        except (ValueError, TypeError) as e:
            pass  # pygame.draw.arc pode rejeitar angulos muito proximos de zero

        # Seta indicadora na ponta do arco
        arrow_angle = ang_rad if self.direction == CCW else -ang_rad
        ax = ox + int(arc_r * math.cos(arrow_angle))
        ay = oy - int(arc_r * math.sin(arrow_angle))
        pygame.draw.circle(surface, arc_col, (ax, ay), 5)

        # Texto do ângulo no centro
        fn_sm = fonts['sm']
        dir_name = "CCW" if self.direction == CCW else "CW"
        lbl = fn_sm.render(f"{self.angle:.0f}°  {dir_name}", True, arc_col)
        bg_surf = pygame.Surface((lbl.get_width()+8, lbl.get_height()+4), pygame.SRCALPHA)
        bg_surf.fill((*cfg.BG2, 200))
        surface.blit(bg_surf, (ox - lbl.get_width()//2 - 4, oy + arc_r + 8))
        surface.blit(lbl, (ox - lbl.get_width()//2, oy + arc_r + 10))

        pygame.draw.circle(surface, cfg.WHITE, (ox, oy), 5)

        # Forma original (cinza transparente)
        orig_s = world_to_screen(SHAPE, cr, cx, cy)
        draw_polygon(surface, orig_s, cfg.GRAY2, width=1,
                     fill=cfg.GRAY2, fill_alpha=20)

        # Forma rotacionada
        c_a = math.cos(math.radians(self.angle))
        s_a = math.sin(math.radians(self.angle))
        if self.direction == CCW:
            R = np.array([[ c_a, -s_a], [ s_a,  c_a]])
        else:
            R = np.array([[ c_a,  s_a], [-s_a,  c_a]])

        rotated   = (R @ SHAPE.T).T
        rotated_s = world_to_screen(rotated, cr, cx, cy)
        col = cfg.BLUE if self.direction == CCW else cfg.ORANGE
        draw_polygon(surface, rotated_s, col, width=2,
                     fill=col, fill_alpha=50)

        # Janelas flutuantes
        dir_name_full = "CCW — Anti-Horário" if self.direction == CCW else "CW — Horário"
        dir_col = cfg.BLUE if self.direction == CCW else cfg.ORANGE
        KW  = (188,140,255)
        CMT = (100,160,100)

        rows_info = [
            ("Rotação 2D",                             cfg.PURPLE),
            ("",                                        cfg.WHITE),
            (f"  Ângulo : {self.angle:.1f}°",          cfg.WHITE),
            (f"  Sentido: {dir_name_full}",            dir_col),
            ("",                                        cfg.WHITE),
            ("  Clique nos botões acima",               cfg.GRAY),
            ("  para trocar o sentido.",                cfg.GRAY),
            ("",                                        cfg.WHITE),
            ("  [ESP] Animar   [R] Reset",              cfg.YELLOW),
            ("  [↑↓]  +/- 5°  [D] Sentido",            cfg.YELLOW),
        ]
        rows_code = [
            ("import numpy as np, math",                KW),
            ("",                                        cfg.WHITE),
            (f"t = math.radians({self.angle:.1f})",    cfg.WHITE),
            ("c, s = math.cos(t), math.sin(t)",        cfg.WHITE),
            ("",                                        cfg.WHITE),
            ("# Anti-Horario (CCW):",                   CMT),
            ("R = [[ c, -s],",                          cfg.WHITE),
            ("     [ s,  c]]",                          cfg.WHITE),
            ("# Horario (CW):",                         CMT),
            ("R = [[ c,  s],",                          cfg.WHITE),
            ("     [-s,  c]]",                          cfg.WHITE),
            ("",                                        cfg.WHITE),
            ("P_novo = np.array(R) @ P",               cfg.WHITE),
        ]

        def _content(win, surf):
            if   win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_code: draw_rows_in_win(surf, win, rows_code)

        self._mgr.draw_managed(surface, fonts, _content)
