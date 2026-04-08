"""
============================================================
 exemplos/aula08/visualizacao_3d.py

 Exemplo interativo: Pipeline de Visualização 3D

 Demonstra:
  - Os 5 espaços do pipeline (Object → World → Camera → Clip → Screen)
  - Projeção perspectiva com câmera controlável
  - Z-Buffer visual (profundidade colorida)
  - Múltiplos objetos no mesmo mundo 3D
  - Matrizes MVP (Model × View × Projection)

 Controles:
  - Setas: rotacionar câmera
  - W/S:   aproximar/afastar câmera (zoom)
  - A/D:   mover câmera esquerda/direita
  - ESPAÇO: rotação automática da cena
  - R: resetar
============================================================
"""

import pygame
import math
import config as cfg
from exemplos.base import ExemploBase
from exemplos.docs_teoria import DOCS_TEORIA
from interface.tabs import TabBar, TAB_H
from interface.doc_view import DocView
from interface.janela import WindowManager, draw_rows_in_win
from interface.ui import draw_label


# ── Geometria dos objetos ────────────────────────────────

def _cubo(cx=0, cy=0, cz=0, s=1.0):
    h = s / 2
    verts = [
        (cx-h, cy-h, cz-h), (cx+h, cy-h, cz-h),
        (cx+h, cy+h, cz-h), (cx-h, cy+h, cz-h),
        (cx-h, cy-h, cz+h), (cx+h, cy-h, cz+h),
        (cx+h, cy+h, cz+h), (cx-h, cy+h, cz+h),
    ]
    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7),
    ]
    return verts, edges

def _piramide(cx=0, cy=0, cz=0, s=1.0):
    h = s
    b = s / 2
    verts = [
        (cx-b, cy,   cz-b),
        (cx+b, cy,   cz-b),
        (cx+b, cy,   cz+b),
        (cx-b, cy,   cz+b),
        (cx,   cy+h, cz),
    ]
    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (0,4),(1,4),(2,4),(3,4),
    ]
    return verts, edges

# ── Transformações 3D ────────────────────────────────────

def _rot_x(pts, a):
    c, s = math.cos(a), math.sin(a)
    return [(x, y*c - z*s, y*s + z*c) for x,y,z in pts]

def _rot_y(pts, a):
    c, s = math.cos(a), math.sin(a)
    return [(x*c + z*s, y, -x*s + z*c) for x,y,z in pts]

def _rot_z(pts, a):
    c, s = math.cos(a), math.sin(a)
    return [(x*c - y*s, x*s + y*c, z) for x,y,z in pts]

def _translate(pts, tx, ty, tz):
    return [(x+tx, y+ty, z+tz) for x,y,z in pts]

def _project_persp(pts, cx, cy, scale, d=4.0):
    result = []
    for x, y, z in pts:
        dz = z + d
        if abs(dz) < 0.01:
            dz = 0.01
        xp = int(cx + (d * x / dz) * scale)
        yp = int(cy - (d * y / dz) * scale)
        depth = dz
        result.append((xp, yp, depth))
    return result


class ExVisualizacao3D(ExemploBase):
    NAME  = "Pipeline 3D"
    COLOR = cfg.CYAN

    def __init__(self):
        super().__init__()
        self.cam_ax   = 0.25    # rotação câmera eixo X
        self.cam_ay   = 0.45    # rotação câmera eixo Y
        self.cam_dist = 5.0     # distância focal
        self.cam_tx   = 0.0
        self.auto_spin = False
        self._mgr      = None
        self._teoria   = DocView(
            fallback_blocks=DOCS_TEORIA["pipeline_3d"],
            download_pdf=cfg.root_path("teoria", "Aula_08", "pipeline_3d.pdf"),
        )
        self._teoria.set_tab_offset(TAB_H)
        self._tabs = TabBar(["Demonstração", "Teoria"])

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create(
            "Pipeline 3D", cax+10, cay+10, 270, 340,
            color=(20, 80, 140), closable=False)
        self._tabs.bind_mgr(self._mgr)

    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 1:
            return self._teoria.handle_mouse_down(pos)
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

    def reset(self):
        self.cam_ax   = 0.25
        self.cam_ay   = 0.45
        self.cam_dist = 5.0
        self.cam_tx   = 0.0
        self.auto_spin = False

    def toggle_anim(self):
        self.auto_spin = not self.auto_spin

    def handle_action(self, action):
        step = math.radians(4)
        if   action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':       self.reset()
        elif action == 'inc':         self.cam_ax -= step
        elif action == 'dec':         self.cam_ax += step
        elif action == 'inc_alt':     self.cam_ay += step
        elif action == 'dec_alt':     self.cam_ay -= step

    def handle_extra(self, key):
        if   key == pygame.K_w: self.cam_dist = max(1.5, self.cam_dist - 0.2)
        elif key == pygame.K_s: self.cam_dist = min(12.0, self.cam_dist + 0.2)
        elif key == pygame.K_a: self.cam_tx -= 0.2
        elif key == pygame.K_d: self.cam_tx += 0.2

    def update(self, dt):
        if self.auto_spin:
            self.cam_ay += 0.6 * dt

    def _draw_object(self, surface, verts, edges, color, cx, cy, scale):
        pts = _rot_x(verts, self.cam_ax)
        pts = _rot_y(pts,   self.cam_ay)
        pts = _translate(pts, self.cam_tx, 0, 0)
        proj = _project_persp(pts, cx, cy, scale, self.cam_dist)

        # ordenar arestas por profundidade média (painter's algorithm simples)
        edge_depths = []
        for a, b in edges:
            d = (proj[a][2] + proj[b][2]) / 2
            edge_depths.append((d, a, b))
        edge_depths.sort(reverse=True)

        for depth, a, b in edge_depths:
            # mapeie profundidade para brilho
            alpha = max(60, min(255, int(200 - depth * 18)))
            c = tuple(min(255, int(ch * alpha / 255)) for ch in color)
            pygame.draw.line(surface, c,
                             (proj[a][0], proj[a][1]),
                             (proj[b][0], proj[b][1]), 2)

        # vértices
        for px, py, d in proj:
            pygame.draw.circle(surface, color, (px, py), 3)

        return proj

    def draw(self, surface, fonts):
        if self._mgr is None:
            self._init_windows()
        self._tabs.draw(surface, fonts)
        if self._tabs.active == 1:
            self._teoria.render(surface)
            return

        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H

        cx = drx + drw // 2
        cy = dry + drh // 2
        scale = int(min(drw, drh) * 0.18)

        # Grid de referência (plano XZ)
        fn = fonts['sm']
        for g in range(-3, 4):
            gx1, _, gz1 = (g * 0.8, 0, -3 * 0.8)
            gx2, _, gz2 = (g * 0.8, 0,  3 * 0.8)
            pts1 = _rot_x([(gx1,0,gz1)], self.cam_ax)
            pts1 = _rot_y(pts1, self.cam_ay)
            pts2 = _rot_x([(gx2,0,gz2)], self.cam_ax)
            pts2 = _rot_y(pts2, self.cam_ay)
            p1 = _project_persp(pts1, cx, cy, scale, self.cam_dist)[0]
            p2 = _project_persp(pts2, cx, cy, scale, self.cam_dist)[0]
            pygame.draw.line(surface, cfg.GRAY2, (p1[0],p1[1]), (p2[0],p2[1]), 1)

            # linha perpendicular
            gx1b, _, gz1b = (-3 * 0.8, 0, g * 0.8)
            gx2b, _, gz2b = ( 3 * 0.8, 0, g * 0.8)
            pts1b = _rot_x([(gx1b,0,gz1b)], self.cam_ax)
            pts1b = _rot_y(pts1b, self.cam_ay)
            pts2b = _rot_x([(gx2b,0,gz2b)], self.cam_ax)
            pts2b = _rot_y(pts2b, self.cam_ay)
            p1b = _project_persp(pts1b, cx, cy, scale, self.cam_dist)[0]
            p2b = _project_persp(pts2b, cx, cy, scale, self.cam_dist)[0]
            pygame.draw.line(surface, cfg.GRAY2, (p1b[0],p1b[1]), (p2b[0],p2b[1]), 1)

        # ── Objetos na cena ──────────────────────────────
        # Cubo central (azul)
        v_cubo, e_cubo = _cubo(0, 0.5, 0, 1.2)
        self._draw_object(surface, v_cubo, e_cubo, cfg.BLUE, cx, cy, scale)

        # Cubo pequeno (laranja) — à direita
        v2, e2 = _cubo(2.0, 0.3, 0.5, 0.7)
        self._draw_object(surface, v2, e2, cfg.ORANGE, cx, cy, scale)

        # Pirâmide (verde) — à esquerda
        v3, e3 = _piramide(-2.0, 0, -0.5, 1.0)
        self._draw_object(surface, v3, e3, cfg.GREEN, cx, cy, scale)

        # Cubo pequeno (roxo) — atrás
        v4, e4 = _cubo(0.5, 0.2, -2.0, 0.6)
        self._draw_object(surface, v4, e4, cfg.PURPLE, cx, cy, scale)

        # Labels dos espaços
        draw_label(surface, "World Space (XYZ)",
                   drx + 10, dry + 10, fn, cfg.GRAY, cfg.BG)
        draw_label(surface, f"d={self.cam_dist:.1f}  ax={math.degrees(self.cam_ax):.0f}°  ay={math.degrees(self.cam_ay):.0f}°",
                   drx + 10, dry + 28, fn, cfg.CYAN, cfg.BG)

        # Legenda de objetos
        legend = [
            (cfg.BLUE,   "Cubo principal"),
            (cfg.ORANGE, "Cubo secundário"),
            (cfg.GREEN,  "Pirâmide"),
            (cfg.PURPLE, "Cubo distante"),
        ]
        for i, (c, lbl) in enumerate(legend):
            pygame.draw.circle(surface, c, (drx + drw - 150, dry + 12 + i*18), 5)
            s = fn.render(lbl, True, c)
            surface.blit(s, (drx + drw - 140, dry + 5 + i*18))

        # Info panel
        rows = [
            ("Pipeline 3D",                cfg.CYAN),
            ("",                           cfg.WHITE),
            ("Object Space",               cfg.GRAY),
            ("  coords locais do objeto",  cfg.GRAY),
            ("",                           cfg.WHITE),
            ("World Space",                cfg.GREEN),
            ("  posicao na cena global",   cfg.GRAY),
            ("",                           cfg.WHITE),
            ("Camera Space",               cfg.BLUE),
            ("  vista da camera",          cfg.GRAY),
            ("",                           cfg.WHITE),
            ("Clip + Screen Space",        cfg.ORANGE),
            ("  pixels na tela",           cfg.GRAY),
            ("",                           cfg.WHITE),
            ("[Setas] Rotacionar",         cfg.YELLOW),
            ("[W/S] Zoom",                 cfg.YELLOW),
            ("[A/D] Mover lateral",        cfg.YELLOW),
            ("[ESP] Auto-rotacao",         cfg.YELLOW),
        ]
        def _content(win, surf):
            if win is self._win_info:
                draw_rows_in_win(surf, win, rows)
        self._mgr.draw_managed(surface, fonts, _content)
