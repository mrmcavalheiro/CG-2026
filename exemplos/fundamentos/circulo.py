"""
============================================================
 exemplos/fundamentos/circulo.py

 Exemplo interativo: Gerando um Círculo com Seno e Cosseno
 - Mostra como N pontos equidistantes formam um círculo
 - Anima a construção ponto a ponto
 - Exibe a fórmula paramétrica e o código Python
 - Permite ajustar o número de pontos e o raio
 - Texto explicativo detalhado integrado ao canvas
============================================================
"""

import pygame
import math
import config as cfg
from exemplos.base    import ExemploBase
from interface.tabs   import TabBar, TAB_H
from interface.doc_view import DocView
from interface.janela import WindowManager
from interface.ui     import draw_label, draw_circle_alpha



class ExCirculo(ExemploBase):
    NAME  = "Círculo com sen/cos"
    COLOR = cfg.GREEN

    SPEED = 45.0   # graus por segundo na animação de construção

    def __init__(self):
        super().__init__()
        self.n_points  = 24
        self.radius    = 140
        self.build_ang = 0.0
        self.running   = True
        self.complete  = False
        self.flash     = 0.0
        self._mgr      = None
        self._teoria   = DocView(cfg.root_path("teoria", "Fundamentos", "circulo.pdf"))
        self._teoria.set_tab_offset(TAB_H)
        self._tabs     = TabBar(["Demonstração", "Teoria"])

    def _init_windows(self):
        cr = cfg.canvas_rect()
        cax, cay, caw, cah = cr
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Circulo — Controles",
            cax+10, cay+10, 240, 255, color=(20,100,50), closable=False)
        self._win_teoria = self._mgr.create("Como Gerar um Circulo",
            cax+caw-290, cay+10, 275, 265, color=(20,60,120), closable=False)
        self._win_code = self._mgr.create("Python — math",
            cax+10, cay+cah-215, 265, 205, color=(60,40,120), closable=False)
        self._tabs.bind_mgr(self._mgr)

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

    def reset(self):
        self.build_ang = 0.0
        self.running   = True
        self.complete  = False

    def toggle_anim(self):
        if self.complete:
            self.reset()
        else:
            self.running = not self.running

    def handle_action(self, action):
        if action == 'toggle_anim':
            self.toggle_anim()
        elif action == 'reset':
            self.reset()
        elif action == 'inc':
            self.n_points = min(self.n_points + 1, 72)
            self.flash = 0.4
            self.reset()
        elif action == 'dec':
            self.n_points = max(self.n_points - 1, 3)
            self.flash = 0.4
            self.reset()
        elif action == 'inc_alt':
            self.radius = min(self.radius + 10, 200)
            self.flash = 0.4
        elif action == 'dec_alt':
            self.radius = max(self.radius - 10, 40)
            self.flash = 0.4

    def update(self, dt):
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)
        if self.running and not self.complete:
            self.build_ang += self.SPEED * dt
            if self.build_ang >= 360.0:
                self.build_ang = 360.0
                self.complete  = True
                self.running   = False

    def draw(self, surface, fonts):
        cr_full = cfg.canvas_rect()
        # Fundo já pintado pelo _draw() principal

        # Zona de desenho (direita do divisor, abaixo das abas)
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cr  = (drx, dry, drw, drh)
        cax, cay, caw, cah = drx, dry, drw, drh

        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        # Teoria: PDF
        if self._tabs.active == 1:
            self._teoria.render(surface)
            return

        cax, cay, caw, cah = cr
        cay += TAB_H
        cah -= TAB_H

        # ── centro do círculo ────────────────────
        cx = cax + int(caw * 0.38)
        cy = cay + cah // 2
        R  = self.radius

        # ── quantos pontos já foram calculados ───
        n_done = int(self.n_points * self.build_ang / 360.0)
        n_done = max(0, min(n_done, self.n_points))

        # ════════════════════════════════════════
        #  1. EIXOS E GUIAS
        # ════════════════════════════════════════
        pygame.draw.line(surface, cfg.GRAY2,
                         (cax + 20, cy), (cax + int(caw * 0.72), cy), 1)
        pygame.draw.line(surface, cfg.GRAY2,
                         (cx, cay + 20), (cx, cay + cah - 20), 1)

        # círculo guia (tracejado)
        for a in range(0, 360, 4):
            rad = math.radians(a)
            px  = cx + int(R * math.cos(rad))
            py  = cy - int(R * math.sin(rad))
            pygame.draw.circle(surface, cfg.BORDER, (px, py), 1)

        # label raio
        pygame.draw.line(surface, (*cfg.GRAY2, 120),
                         (cx, cy), (cx + R, cy), 1)
        draw_label(surface, f"R={R}", cx + R // 2 - 15, cy + 6,
                   fonts['sm'], cfg.GRAY2)

        # ════════════════════════════════════════
        #  2. PONTOS DO CÍRCULO (construção animada)
        # ════════════════════════════════════════
        pts = []
        step_ang = 360.0 / self.n_points

        for i in range(n_done + 1):
            ang_deg = i * step_ang
            rad     = math.radians(ang_deg)
            px      = cx + int(R * math.cos(rad))
            py      = cy - int(R * math.sin(rad))
            pts.append((px, py))

            if i < n_done:
                # raio tracejado até o ponto
                for t in range(0, 10, 2):
                    fx = cx + int((R * t / 10) * math.cos(rad))
                    fy = cy - int((R * t / 10) * math.sin(rad))
                    draw_circle_alpha(surface, cfg.GRAY2, (fx, fy), 1, alpha=60)

                # ponto no círculo
                color = cfg.GREEN if i % 3 == 0 else cfg.CYAN
                pygame.draw.circle(surface, color, (px, py), 5)
                pygame.draw.circle(surface, cfg.WHITE, (px, py), 5, 1)

                # label do ângulo para os primeiros pontos
                if i <= 4 or (i == n_done - 1 and i > 4):
                    a_str = f"{ang_deg:.0f}°"
                    draw_label(surface, a_str,
                               px + 6, py - 14, fonts['sm'], cfg.YELLOW, cfg.BG2)

        # linhas conectando pontos consecutivos
        if len(pts) > 2:
            pygame.draw.lines(surface, cfg.GREEN, self.complete,
                              pts[:-1], 2)

        # ponto atual (frente da construção)
        if n_done < self.n_points and n_done >= 0:
            rad_cur = math.radians(n_done * step_ang)
            px_cur  = cx + int(R * math.cos(rad_cur))
            py_cur  = cy - int(R * math.sin(rad_cur))

            # raio do ponto atual em destaque
            pygame.draw.line(surface, cfg.YELLOW,
                             (cx, cy), (px_cur, py_cur), 2)

            # componentes cos e sen do ponto atual
            pygame.draw.line(surface, cfg.ORANGE,
                             (cx, cy), (px_cur, cy), 2)
            pygame.draw.line(surface, cfg.BLUE,
                             (px_cur, cy), (px_cur, py_cur), 2)

            draw_label(surface, f"cos", cx + int(R * math.cos(rad_cur)) // 2,
                       cy + 6, fonts['sm'], cfg.ORANGE, cfg.BG2)
            draw_label(surface, f"sen", px_cur + 4,
                       cy - int(R * math.sin(rad_cur)) // 2,
                       fonts['sm'], cfg.BLUE, cfg.BG2)

            pygame.draw.circle(surface, cfg.YELLOW, (px_cur, py_cur), 8)
            pygame.draw.circle(surface, cfg.WHITE,  (px_cur, py_cur), 8, 2)

        # ── origem ──────────────────────────────
        pygame.draw.circle(surface, cfg.WHITE, (cx, cy), 4)

        # ── status: completo ─────────────────────
        if self.complete:
            msg = "Circulo completo! [ESP] para reiniciar"
            s   = fonts['sm'].render(msg, True, cfg.GREEN)
            surface.blit(s, (cx - s.get_width() // 2,
                              cy + R + 18))

        # ═══════════════════════════════════════
        #  JANELAS FLUTUANTES
        #  Ordem: 1) fundos  2) conteudo  3) titlebars
        # ═══════════════════════════════════════
        if self._mgr is None:
            self._init_windows()

        nc  = cfg.YELLOW if self.flash > 0 else cfg.WHITE
        prog = int(self.build_ang / 360 * 100)
        CMT = (100,140,100); KW = (188,140,255)
        fn  = fonts['sm']
        lh  = fn.get_height() + 5

        # Prepara linhas de conteúdo
        rows_info = [
            ("Circulo com sen e cos",                    cfg.GREEN),
            (f"  N de pontos: {self.n_points}",          nc),
            (f"  Raio R:      {self.radius} px",         nc),
            (f"  Progresso:   {prog}%",                  cfg.CYAN),
            ("",                                         cfg.WHITE),
            (f"  passo = 360/{self.n_points} = {360/self.n_points:.1f} graus", cfg.GRAY),
            ("",                                         cfg.WHITE),
            ("[ESP] Animar / Reiniciar",                 cfg.YELLOW),
            ("[R] Reset",                                cfg.YELLOW),
            ("[Cima/Baixo] N de pontos",                 cfg.YELLOW),
            ("[Esq/Dir] Raio",                           cfg.YELLOW),
        ]
        rows_teoria = [
            ("Como gerar um circulo?",          cfg.GREEN),
            ("",                               cfg.WHITE),
            ("Equacao parametrica:",            cfg.GRAY),
            ("  x = R * cos(t)",               cfg.ORANGE),
            ("  y = R * sen(t)",               cfg.BLUE),
            ("",                               cfg.WHITE),
            ("t varia de 0 a 360 graus.",      cfg.GRAY),
            ("",                               cfg.WHITE),
            ("Dividindo em N partes iguais",   cfg.GRAY),
            ("obtemos N pontos no circulo.",   cfg.GRAY),
            ("",                               cfg.WHITE),
            ("Maior N = circulo mais suave.",  cfg.GRAY),
            ("Menor N = poligono visivel.",    cfg.GRAY),
        ]

        rows_code = [
            ("import math",                              KW),
            ("",                                        cfg.WHITE),
            (f"N = {self.n_points}  # num pontos",      cfg.WHITE),
            (f"R = {self.radius}    # raio",            cfg.WHITE),
            ("pontos = []",                              cfg.WHITE),
            ("",                                        cfg.WHITE),
            ("for i in range(N):",                      KW),
            ("  t = math.radians(360*i/N)",             cfg.WHITE),
            ("  x = R * math.cos(t)",                   cfg.WHITE),
            ("  y = R * math.sin(t)",                   cfg.WHITE),
            ("  pontos.append((x, y))",                 cfg.WHITE),
        ]

        def _content(win, surf):
            from interface.janela import draw_rows_in_win
            if   win is self._win_info:   draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_teoria: draw_rows_in_win(surf, win, rows_teoria)
            elif win is self._win_code:   draw_rows_in_win(surf, win, rows_code)

        self._mgr.draw_managed(surface, fonts, _content)


