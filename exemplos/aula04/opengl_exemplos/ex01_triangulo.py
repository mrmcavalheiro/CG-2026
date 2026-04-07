"""
============================================================
 ex01_triangulo.py — Triangulo Colorido (Projeto 01)
============================================================
"""
import pygame
import math
import config as cfg
from exemplos.base  import ExemploBase
from interface.tabs import TabBar, TAB_H
from interface.janela import WindowManager, draw_rows_in_win
from interface.ui   import draw_grid, draw_axes
from exemplos.aula04.opengl_exemplos._code_viewer import CodeViewer
from exemplos.aula04.opengl_exemplos._teoria      import make_teoria_doc

_ARQUIVOS = {
    "src/exemplo.py": [
        '"""',
        'Sistema de coordenadas 3D OpenGL:',
        '  X cresce para direita, Y para cima, Z para frente.',
        '"""',
        "from OpenGL.GL   import *",
        "from OpenGL.GLUT import *",
        "from OpenGL.GLU  import *",
        "",
        "class Exemplo:",
        "    def __init__(self):",
        '        """Inicializa janela e configura camera."""',
        "        glutInit()",
        "        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)",
        "        glutInitWindowSize(800, 600)",
        '        glutCreateWindow(b"PyOpenGL - Exemplo 01")',
        "        self.inicializar()",
        "        glutDisplayFunc(self.desenhar)",
        "        glutKeyboardFunc(self.teclado)",
        "        glutIdleFunc(self.desenhar)",
        "",
        "    def inicializar(self):",
        "        glClearColor(0,0,0,1)      # fundo preto",
        "        glEnable(GL_DEPTH_TEST)    # z-buffer",
        "        glMatrixMode(GL_PROJECTION)",
        "        glLoadIdentity()",
        "        gluPerspective(45, 800/600, 0.1, 50.0)  # frustum",
        "        glMatrixMode(GL_MODELVIEW)",
        "        glTranslatef(0.0, 0.0, -5) # afasta camera",
        "",
        "    def desenhar(self):",
        "        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)",
        "        glBegin(GL_TRIANGLES)",
        "        glColor3f(1, 0, 0)        # vermelho",
        "        glVertex3f(-1, -1, 0)     # vertice 1",
        "        glColor3f(0, 1, 0)        # verde",
        "        glVertex3f( 1, -1, 0)     # vertice 2",
        "        glColor3f(0, 0, 1)        # azul",
        "        glVertex3f( 0,  1, 0)     # vertice 3",
        "        glEnd()",
        "        glutSwapBuffers()",
        "",
        "    def teclado(self, tecla, x, y):",
        "        if tecla == b'\\x1b': glutLeaveMainLoop()",
        "",
        "    def executar(self):",
        "        glutMainLoop()",
    ],
}


class ExOpenGL01(ExemploBase):
    NAME  = "Ex01 — Triangulo"
    COLOR = cfg.GREEN

    def __init__(self):
        super().__init__()
        self._tabs   = TabBar(["Demonstração", "Resolução", "Teoria"])
        self._viewer = CodeViewer(_ARQUIVOS)
        self._teoria = make_teoria_doc("ex01_triangulo")
        self._teoria.set_tab_offset(TAB_H)
        self._mgr    = None
        self._angle  = 0.0
        self._anim   = True

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Triangulo — Conceitos",
            cax+10, cay+10, 310, 260, color=(20,100,40), closable=False)
        self._win_code = self._mgr.create("Fragmento Principal",
            cax+10, cay+285, 310, 220, color=(60,40,120), closable=False)

    def reset(self): self._angle = 0.0; self._anim = True
    def toggle_anim(self): self._anim = not self._anim
    def update(self, dt):
        if self._anim: self._angle = (self._angle + 50*dt) % 360

    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 1: return self._viewer.handle_mouse_down(pos)
        if self._tabs.active == 2: return self._teoria.handle_mouse_down(pos, cfg.canvas_rect())
        if self._tabs.active == 0 and self._mgr: return self._mgr.handle_mouse_down(pos)
        return False
    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 1: self._viewer.handle_mouse_move(pos)
        elif self._tabs.active == 2: self._teoria.handle_mouse_move(pos)
        elif self._mgr: self._mgr.handle_mouse_move(pos)
    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up(); self._viewer.handle_mouse_up()
        self._teoria.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)
    def handle_scroll(self, dy):
        if self._tabs.active == 1: self._viewer.handle_scroll(dy)
        elif self._tabs.active == 2: self._teoria.handle_scroll(dy)
        elif self._mgr: self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)

    def draw(self, surface, fonts):
        if self._mgr is None: self._init_windows()
        self._tabs.draw(surface, fonts)
        if self._tabs.active == 1: self._viewer.render(surface, fonts); return
        if self._tabs.active == 2: self._teoria.render(surface); return

        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cr = (drx, dry, drw, drh)
        cx = drw//2; cy = drh//2
        draw_grid(surface, cr, cx, cy)
        draw_axes(surface, cr, cx, cy, font=fonts['sm'])

        # Triangulo animado
        ox = drx + cx; oy = dry + cy
        a  = math.radians(self._angle)
        pts = []
        verts = [(-80,-60,0), (80,-60,0), (0,90,0)]
        colors = [(255,60,60), (60,220,60), (60,100,255)]
        for vx,vy,_ in verts:
            rx = vx*math.cos(a) - vy*math.sin(a)*0.4
            ry = vy*math.cos(a*0.5)
            pts.append((int(ox+rx), int(oy-ry)))

        # fill with gradient simulation
        if len(pts) == 3:
            pygame.draw.polygon(surface, (40,80,60), pts)
            pygame.draw.polygon(surface, (80,160,120), pts, 2)
            for i,pt in enumerate(pts):
                pygame.draw.circle(surface, colors[i], pt, 7)
                fn_s = fonts['sm']
                labels = ["V1(-1,-1,0)", "V2(1,-1,0)", "V3(0,1,0)"]
                t = fn_s.render(labels[i], True, colors[i])
                surface.blit(t, (pt[0]+9, pt[1]-8))

        # Centroid
        gcx = sum(p[0] for p in pts)//3
        gcy = sum(p[1] for p in pts)//3
        fn_s = fonts['sm']
        lbl = fn_s.render(f"rot={self._angle:.0f}°", True, cfg.YELLOW)
        surface.blit(lbl, (gcx - lbl.get_width()//2, gcy - 10))

        rows_info = [
            ("Triangulo 3D",                    cfg.GREEN),
            ("",                                cfg.WHITE),
            ("  glBegin(GL_TRIANGLES)",         cfg.CYAN),
            ("  3 vertices com cores proprias", cfg.GRAY),
            ("  Interpolacao automatica",       cfg.GRAY),
            ("",                                cfg.WHITE),
            ("Sistema de coords:",              cfg.BLUE),
            ("  X → direita",                  cfg.GRAY),
            ("  Y → cima",                     cfg.GRAY),
            ("  Z → observador",               cfg.GRAY),
            ("",                               cfg.WHITE),
            ("[ESP] Animar  [R] Reset",         cfg.YELLOW),
        ]
        rows_code = [
            ("glBegin(GL_TRIANGLES)",           cfg.CYAN),
            ("  glColor3f(1, 0, 0)",            (255, 80, 80)),
            ("  glVertex3f(-1, -1, 0)",         cfg.WHITE),
            ("  glColor3f(0, 1, 0)",            (80, 220, 80)),
            ("  glVertex3f( 1, -1, 0)",         cfg.WHITE),
            ("  glColor3f(0, 0, 1)",            (80, 120, 255)),
            ("  glVertex3f( 0,  1, 0)",         cfg.WHITE),
            ("glEnd()",                         cfg.CYAN),
        ]

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_code: draw_rows_in_win(surf, win, rows_code)
        self._mgr.draw_managed(surface, fonts, _content)
