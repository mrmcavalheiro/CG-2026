"""
============================================================
 exemplos/fundamentos/seno_cosseno.py
 Seno e Cosseno — padrão Aula 04 com DocView para Teoria
============================================================
"""
import math
import pygame
import config as cfg
from exemplos.base    import ExemploBase
from interface.janela import WindowManager, draw_rows_in_win
from interface.tabs   import TabBar, TAB_H
from interface.doc_view import DocView

TABS    = ["Demonstração", "Teoria"]


class ExSenoCosseno(ExemploBase):
    NAME  = "Seno e Cosseno"
    COLOR = cfg.CYAN
    SPEED = 60.0

    def __init__(self):
        super().__init__()
        self.angle     = 0.0
        self.running   = True
        self.history_s = []
        self.history_c = []
        self.MAX_HIST  = 360
        self._mgr      = None
        self._tabs     = TabBar(["Demonstração", "Teoria"])
        self._teoria   = DocView(cfg.root_path("teoria", "Fundamentos", "seno_cosseno.pdf"))
        self._teoria.set_tab_offset(TAB_H)
        self._win_info   = None
        self._win_teoria = None
        self._win_code   = None
        self._win_id     = None

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info   = self._mgr.create("Valores em Tempo Real",
            cax+10, cay+10, 240, 230, color=(30,120,180), closable=False)
        self._win_teoria = self._mgr.create("Teoria — Círculo Unitário",
            cax+caw-320, cay+10, 310, 220, color=(20,100,80), closable=False)
        self._win_code   = self._mgr.create("Python — math",
            cax+10, cay+cah-220, 260, 210, color=(60,40,120), closable=False)
        self._win_id     = self._mgr.create("Identidade Fundamental",
            cax+caw-240, cay+cah-150, 225, 135, color=(120,80,20), closable=False)
        self._tabs.bind_mgr(self._mgr)

    def reset(self):
        self.angle = 0.0; self.running = True
        self.history_s = []; self.history_c = []

    def toggle_anim(self): self.running = not self.running

    def handle_action(self, action):
        if   action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':       self.reset()
        elif action == 'inc':         self.angle = (self.angle + 5) % 360
        elif action == 'dec':         self.angle = (self.angle - 5) % 360

    def handle_mouse_down(self, pos):
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
        else:
            self._tabs.handle_scroll(dy)

    def update(self, dt):
        if self.running:
            self.angle = (self.angle + self.SPEED * dt) % 360
        rad = math.radians(self.angle)
        self.history_s.append(math.sin(rad))
        self.history_c.append(math.cos(rad))
        if len(self.history_s) > self.MAX_HIST:
            self.history_s.pop(0); self.history_c.pop(0)

    def draw(self, surface, fonts):
        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        # Teoria: PDF
        if self._tabs.active == 1:
            self._teoria.render(surface)
            return

        self._draw_demo(surface, fonts)

    # ── DEMONSTRAÇÃO ──────────────────────────────────────────
    def _draw_demo(self, surface, fonts):
        import math as _math
        rad   = _math.radians(self.angle)
        sen_v = _math.sin(rad)
        cos_v = _math.cos(rad)
        fn    = fonts['sm']

        cr = cfg.canvas_rect()
        cax, cay, caw, cah = cr

        # Zona de desenho
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cr = (drx, dry, drw, drh)
        cx = drw // 2
        cy = drh // 2

        # Geometria
        circ_cx  = drx + int(drw * 0.35)
        circ_cy  = dry + drh // 2
        R        = min(drw, drh) // 5
        wave_x0  = drx + int(drw * 0.56)
        wave_w   = int(drw * 0.42)
        wave_cy  = dry + drh // 2
        wave_amp = R

        # Círculo
        pygame.draw.line(surface, (*cfg.GRAY2,180),
            (circ_cx-R-25, circ_cy), (circ_cx+R+25, circ_cy), 1)
        pygame.draw.line(surface, (*cfg.GRAY2,180),
            (circ_cx, circ_cy-R-25), (circ_cx, circ_cy+R+25), 1)
        pygame.draw.circle(surface, cfg.BORDER, (circ_cx, circ_cy), R, 1)

        px = circ_cx + int(R * cos_v)
        py = circ_cy  - int(R * sen_v)

        pygame.draw.line(surface, cfg.WHITE, (circ_cx, circ_cy), (px, py), 2)
        for i in range(0, abs(px-circ_cx), 6):
            sx = circ_cx + (i if px > circ_cx else -i)
            pygame.draw.circle(surface, cfg.ORANGE, (sx, circ_cy), 1)
        for i in range(0, abs(py-circ_cy), 6):
            sy = circ_cy + (i if py > circ_cy else -i)
            pygame.draw.circle(surface, cfg.BLUE, (circ_cx, sy), 1)
        pygame.draw.line(surface, cfg.ORANGE, (circ_cx, circ_cy), (px, circ_cy), 2)
        pygame.draw.line(surface, cfg.BLUE,   (px, circ_cy), (px, py), 2)
        pygame.draw.circle(surface, cfg.CYAN,  (px, py), 7)
        pygame.draw.circle(surface, cfg.WHITE, (px, py), 7, 2)
        pygame.draw.circle(surface, cfg.WHITE, (circ_cx, circ_cy), 4)

        arc_r = R // 3
        if abs(rad) > 0.05:
            try:
                pygame.draw.arc(surface, cfg.YELLOW,
                    pygame.Rect(circ_cx-arc_r, circ_cy-arc_r, arc_r*2, arc_r*2),
                    min(0,rad), max(0,rad), 2)
            except (ValueError, TypeError): pass  # valores extremos de seno/cosseno

        def lbl(txt, x, y, c):
            s  = fn.render(txt, True, c)
            bg = pygame.Surface((s.get_width()+6, s.get_height()+2), pygame.SRCALPHA)
            bg.fill((*cfg.BG2, 200)); surface.blit(bg, (x-3, y-1)); surface.blit(s, (x, y))

        lbl(f"{self.angle:.0f}°",
            circ_cx+int(arc_r*1.4*_math.cos(rad/2))-10,
            circ_cy-int(arc_r*1.4*_math.sin(rad/2))-8, cfg.YELLOW)
        lbl(f"cos={cos_v:+.2f}", (circ_cx+px)//2-28, circ_cy+8, cfg.ORANGE)
        lbl(f"sen={sen_v:+.2f}", px+8, (circ_cy+py)//2-7, cfg.BLUE)
        lbl(f"P({cos_v:+.2f},{sen_v:+.2f})", px+10, py-18, cfg.CYAN)

        # Ondas
        if len(self.history_s) > 1:
            pygame.draw.line(surface, cfg.GRAY2,
                (wave_x0, wave_cy-wave_amp-15),(wave_x0, wave_cy+wave_amp+15), 1)
            pygame.draw.line(surface, cfg.GRAY2,
                (wave_x0-5, wave_cy),(wave_x0+wave_w, wave_cy), 1)
            for sgn in (1,-1):
                pygame.draw.line(surface, (*cfg.GRAY2,80),
                    (wave_x0, wave_cy-sgn*wave_amp),
                    (wave_x0+wave_w, wave_cy-sgn*wave_amp), 1)
            n    = len(self.history_s)
            step = wave_w / self.MAX_HIST
            pts_s = [(wave_x0+int(i*step), int(wave_cy-sv*wave_amp))
                     for i,(sv,_) in enumerate(zip(self.history_s,self.history_c))]
            pts_c = [(wave_x0+int(i*step), int(wave_cy-cv*wave_amp))
                     for i,(_,cv) in enumerate(zip(self.history_s,self.history_c))]
            if len(pts_s) > 1: pygame.draw.lines(surface, cfg.BLUE,   False, pts_s, 2)
            if len(pts_c) > 1: pygame.draw.lines(surface, cfg.ORANGE, False, pts_c, 2)
            cur_x = wave_x0 + int((n-1)*step)
            pygame.draw.circle(surface, cfg.BLUE,
                (cur_x, int(wave_cy-sen_v*wave_amp)), 5)
            pygame.draw.circle(surface, cfg.ORANGE,
                (cur_x, int(wave_cy-cos_v*wave_amp)), 5)
            pygame.draw.line(surface, (*cfg.BLUE,100),
                (px,py),(cur_x,int(wave_cy-sen_v*wave_amp)), 1)
            lbl("sen(t)", wave_x0+wave_w-50, wave_cy-wave_amp-14, cfg.BLUE)
            lbl("cos(t)", wave_x0+wave_w-50, wave_cy+wave_amp+2,  cfg.ORANGE)

        # Janelas flutuantes
        CMT = (100,140,100); KW = (188,140,255)
        rows_info = [
            (f"  angulo = {self.angle:.1f} deg",         cfg.WHITE),
            (f"  sen({self.angle:.0f}) = {sen_v:+.4f}", cfg.BLUE),
            (f"  cos({self.angle:.0f}) = {cos_v:+.4f}", cfg.ORANGE),
            ("",                                          cfg.WHITE),
            ("Identidade:",                               cfg.GRAY),
            (f"  s²+c² = {sen_v**2+cos_v**2:.4f}",      cfg.GREEN),
            ("",                                          cfg.WHITE),
            ("[ESP] Pausar  [R] Reset",                   cfg.YELLOW),
            ("[↑↓] +/- 5 graus",                         cfg.YELLOW),
        ]
        rows_teoria = [
            ("Para angulo t, ponto P no circulo",     cfg.GRAY),
            ("unitario tem coordenadas:",             cfg.GRAY),
            ("",                                      cfg.WHITE),
            ("  x = cos(t)  (horizontal)",           cfg.ORANGE),
            ("  y = sen(t)  (vertical)",             cfg.BLUE),
            ("",                                      cfg.WHITE),
            ("sen²(t) + cos²(t) = 1",                cfg.WHITE),
            ("",                                      cfg.WHITE),
            (f"  {sen_v**2:.4f} + {cos_v**2:.4f} = {sen_v**2+cos_v**2:.4f}", cfg.GREEN),
        ]
        rows_code = [
            ("import math",                              KW),
            ("",                                         cfg.WHITE),
            (f"t = math.radians({self.angle:.1f})",     cfg.WHITE),
            ("s = math.sin(t)",                          cfg.WHITE),
            ("c = math.cos(t)",                          cfg.WHITE),
            ("P = (c, s)",                               cfg.WHITE),
        ]
        rows_id = [
            ("sen²(t) + cos²(t) = 1",                cfg.WHITE),
            ("",                                       cfg.WHITE),
            (f"  {sen_v**2:.4f}   (sen²)",           cfg.BLUE),
            (f"+ {cos_v**2:.4f}   (cos²)",           cfg.ORANGE),
            (f"= {sen_v**2+cos_v**2:.4f}",           cfg.GREEN),
        ]

        def _content(win, surf):
            if   win is self._win_info:   draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_teoria: draw_rows_in_win(surf, win, rows_teoria)
            elif win is self._win_code:   draw_rows_in_win(surf, win, rows_code)
            elif win is self._win_id:     draw_rows_in_win(surf, win, rows_id)

        self._mgr.draw_managed(surface, fonts, _content)
