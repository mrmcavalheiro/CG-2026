"""
============================================================
 exemplos/aula05/proj_ortogonal.py

 Exemplo interativo: Projecao Ortogonal

 Demonstra:
  - Cubo 3D projetado ortogonalmente em 2D
  - Linhas de projecao paralelas
  - Rotacao do cubo para visualizar a projecao
  - Comparacao: vista frontal, lateral e superior
  - Formula: xv = x * escala, yv = y * escala (ignora Z)

 Controles:
  - Setas: rotacionar cubo (X e Y)
  - ESPACO: rotacao automatica
  - R: resetar
============================================================
"""

import pygame
import math
import config as cfg
from exemplos.base import ExemploBase
from interface.ui  import draw_label, draw_circle_alpha
from interface.tabs   import TabBar, TAB_H
from interface.doc_view import DocView
from interface.janela import WindowManager, draw_rows_in_win


# Vertices do cubo unitario centrado na origem
CUBE_VERTS = [
    (-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),   # face traseira
    (-1,-1, 1),(1,-1, 1),(1,1, 1),(-1,1, 1),   # face frontal
]
# Arestas do cubo (indices dos vertices)
CUBE_EDGES = [
    (0,1),(1,2),(2,3),(3,0),   # face traseira
    (4,5),(5,6),(6,7),(7,4),   # face frontal
    (0,4),(1,5),(2,6),(3,7),   # laterais
]


def rot_x(pts, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(x, y*c - z*s, y*s + z*c) for x,y,z in pts]

def rot_y(pts, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(x*c + z*s, y, -x*s + z*c) for x,y,z in pts]



class ExProjOrtogonal(ExemploBase):
    NAME  = "Proj. Ortogonal"
    COLOR = cfg.BLUE

    ESCALA = 80

    def __init__(self):
        super().__init__()
        self.angle_x   = 0.3
        self.angle_y   = 0.5
        self.auto_spin = False
        self._mgr      = None
        self._teoria   = DocView(cfg.root_path("teoria", "Aula_05", "proj_ortogonal.pdf"))
        self._teoria.set_tab_offset(TAB_H)
        self._tabs     = TabBar(["Demonstração", "Teoria"])


    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Projeção Ortogonal",
            cax+10, cay+10, 260, 340, color=(30,80,180), closable=False)
        self._win_code = self._mgr.create("Python",
            cax+10, cay+365, 260, 220, color=(60,40,120), closable=False)
        self._tabs.bind_mgr(self._mgr)


    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 0 and self._mgr:
            return self._mgr.handle_mouse_down(pos)
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 0 and self._mgr:
            self._mgr.handle_mouse_move(pos)

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
        self.angle_x   = 0.3
        self.angle_y   = 0.5
        self.auto_spin = False

    def toggle_anim(self):
        self.auto_spin = not self.auto_spin

    def handle_action(self, action):
        step = math.radians(5)
        if   action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':       self.reset()
        elif action == 'inc':         self.angle_x -= step
        elif action == 'dec':         self.angle_x += step
        elif action == 'inc_alt':     self.angle_y += step
        elif action == 'dec_alt':     self.angle_y -= step

    def update(self, dt):
        if self.auto_spin:
            self.angle_y += 0.8 * dt
            self.angle_x += 0.3 * dt

    def _project_ortho(self, verts, cx, cy, scale):
        """Projecao ortogonal: ignora Z."""
        return [(int(cx + v[0]*scale), int(cy - v[1]*scale))
                for v in verts]

    def draw(self, surface, fonts):
        cr  = cfg.canvas_rect()
        cax, cay, caw, cah = cr

        # Fundo já pintado pelo _draw() principal

        # Ajusta área de conteúdo abaixo das abas
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cax = drx; cay = dry
        caw = drw; cah = drh

        # Rotacionar vertices
        verts = list(CUBE_VERTS)
        verts = rot_x(verts, self.angle_x)
        verts = rot_y(verts, self.angle_y)

        # ── 3 vistas ortogonais ──────────────────────────
        views = [
            ("Vista Frontal\n(ignora Z)",   lambda v: (v[0], v[1]),  cfg.BLUE),
            ("Vista Lateral\n(ignora X)",   lambda v: (-v[2], v[1]), cfg.GREEN),
            ("Vista Superior\n(ignora Y)",  lambda v: (v[0], -v[2]), cfg.PURPLE),
        ]

        view_w = int(caw * 0.25)
        view_h = view_w
        view_y = cay + (cah - view_h) // 2
        scale  = view_w // 3

        for i, (title, proj_fn, color) in enumerate(views):
            vx = cax + 10 + i * (view_w + 15)

            # fundo
            pygame.draw.rect(surface, cfg.BG2,
                             (vx, view_y, view_w, view_h))
            pygame.draw.rect(surface, color,
                             (vx, view_y, view_w, view_h), 1)

            cx_ = vx + view_w // 2
            cy_ = view_y + view_h // 2

            # eixos
            pygame.draw.line(surface, cfg.GRAY2,
                             (vx+5, cy_), (vx+view_w-5, cy_), 1)
            pygame.draw.line(surface, cfg.GRAY2,
                             (cx_, view_y+5), (cx_, view_y+view_h-5), 1)

            # linhas de projecao (tracejadas, de cada vertice)
            for v in verts:
                px2d, py2d = proj_fn(v)
                px = int(cx_ + px2d * scale)
                py = int(cy_ - py2d * scale)
                # linha tracejada da origem ao ponto
                for t in range(0, 8, 3):
                    fx = int(cx_ + px2d * scale * t / 8)
                    fy = int(cy_ - py2d * scale * t / 8)
                    draw_circle_alpha(surface, cfg.GRAY2, (fx, fy), 1, alpha=60)
                pygame.draw.circle(surface, color, (px, py), 3)

            # arestas projetadas
            pts2d = [(int(cx_ + proj_fn(v)[0]*scale),
                      int(cy_ - proj_fn(v)[1]*scale)) for v in verts]
            for a, b in CUBE_EDGES:
                pygame.draw.line(surface, color, pts2d[a], pts2d[b], 2)

            # titulo
            for j, line in enumerate(title.split('\n')):
                s = fonts['sm'].render(line, True, color)
                surface.blit(s, (vx + view_w//2 - s.get_width()//2,
                                  view_y - 34 + j*16))

        # ── Vista 3D perspectiva suave (referencia) ──────
        ref_x = cax + 10 + 3*(view_w+15)
        ref_w = caw - (3*(view_w+15)) - 20
        if ref_w > 80:
            ref_h = view_h
            ref_cy = view_y + ref_h // 2
            ref_cx = ref_x + ref_w // 2

            pygame.draw.rect(surface, cfg.BG2,
                             (ref_x, view_y, ref_w, ref_h))
            pygame.draw.rect(surface, cfg.YELLOW,
                             (ref_x, view_y, ref_w, ref_h), 1)
            s = fonts['sm'].render("3D (referencia)", True, cfg.YELLOW)
            surface.blit(s, (ref_cx - s.get_width()//2, view_y - 20))

            sc3 = ref_w // 4
            # perspectiva simples para o 3D
            def proj3(v):
                d = 3.5
                xp = v[0] / (1 + v[2]/d)
                yp = v[1] / (1 + v[2]/d)
                return (int(ref_cx + xp*sc3), int(ref_cy - yp*sc3))

            pts3d = [proj3(v) for v in verts]
            for a, b in CUBE_EDGES:
                alpha = int(180 + 75 * (verts[a][2] + verts[b][2]) / 2)
                alpha = max(80, min(255, alpha))
                pygame.draw.line(surface, cfg.YELLOW, pts3d[a], pts3d[b], 1)

        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        rows_info = [
            ("Projecao Ortogonal",       cfg.BLUE),
            ("",                        cfg.WHITE),
            ("Ignora a profundidade Z.", cfg.GRAY),
            ("Linhas de projecao",       cfg.GRAY),
            ("sao paralelas entre si.",  cfg.GRAY),
            ("",                        cfg.WHITE),
            ("Formula:",                cfg.CYAN),
            ("  xv = x * escala",       cfg.WHITE),
            ("  yv = y * escala",       cfg.WHITE),
            ("  (Z ignorado!)",         cfg.GRAY),
            ("",                        cfg.WHITE),
            ("[ESP] Rotacao auto",       cfg.YELLOW),
            ("[Setas] Girar cubo",       cfg.YELLOW),
            ("[R] Reset",               cfg.YELLOW),
        ]
        rows_code = [
            ("# Projecao Ortogonal",    (100,140,100)),
            ("def proj_ortho(x,y,z,",  cfg.WHITE),
            ("               escala):", cfg.WHITE),
            ("  # Z e ignorado!",       (100,140,100)),
            ("  xv = cx + x * escala",  cfg.WHITE),
            ("  yv = cy - y * escala",  cfg.WHITE),
            ("  return xv, yv",         cfg.WHITE),
        ]
        def _content(win, surf):
            if   win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_code: draw_rows_in_win(surf, win, rows_code)
        self._mgr.draw_managed(surface, fonts, _content)


