"""
============================================================
 ex02_formas.py — Alternando Formas 3D (Projeto 02)
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
        "from OpenGL.GL   import *",
        "from OpenGL.GLUT import *",
        "from OpenGL.GLU  import *",
        "from src.renderizador import Renderizador",
        "",
        "class Exemplo:",
        "    def __init__(self):",
        "        glutInit()",
        "        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)",
        "        glutInitWindowSize(800, 600)",
        '        glutCreateWindow(b"PyOpenGL - Alternando Formas 3D")',
        "        self.inicializar()",
        "        self.renderizador = Renderizador()",
        "        self.formas = ['triangulo','quadrado','cubo','piramide']",
        "        self.indice_forma = 0     # comeca com triangulo",
        "        glutDisplayFunc(self.desenhar)",
        "        glutKeyboardFunc(self.teclado)",
        "        glutIdleFunc(self.desenhar)",
        "",
        "    def inicializar(self):",
        "        glClearColor(0,0,0,1)",
        "        glEnable(GL_DEPTH_TEST)",
        "        glMatrixMode(GL_PROJECTION)",
        "        glLoadIdentity()",
        "        gluPerspective(45, 800/600, 0.1, 50.0)",
        "        glMatrixMode(GL_MODELVIEW)",
        "        glTranslatef(0.0, 0.0, -5)",
        "",
        "    def desenhar(self):",
        "        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)",
        "        forma = self.formas[self.indice_forma]",
        "        if forma == 'triangulo': self.renderizador.desenhar_triangulo()",
        "        elif forma == 'quadrado': self.renderizador.desenhar_quadrado()",
        "        elif forma == 'cubo':    self.renderizador.desenhar_cubo()",
        "        elif forma == 'piramide':self.renderizador.desenhar_piramide()",
        "        glutSwapBuffers()",
        "",
        "    def teclado(self, tecla, x, y):",
        "        if tecla == b'\\x1b': glutLeaveMainLoop()",
        "        elif tecla == b'q':  # volta",
        "            self.indice_forma = (self.indice_forma - 1) % len(self.formas)",
        "        elif tecla == b'e':  # avanca",
        "            self.indice_forma = (self.indice_forma + 1) % len(self.formas)",
        "",
        "    def executar(self): glutMainLoop()",
    ],
    "src/renderizador.py": [
        "from OpenGL.GL import *",
        "",
        "class Renderizador:",
        "    def desenhar_triangulo(self):",
        "        glBegin(GL_TRIANGLES)",
        "        glColor3f(1,0,0); glVertex3f(-1,-1,0)",
        "        glColor3f(0,1,0); glVertex3f( 1,-1,0)",
        "        glColor3f(0,0,1); glVertex3f( 0, 1,0)",
        "        glEnd()",
        "",
        "    def desenhar_quadrado(self):",
        "        glBegin(GL_QUADS)",
        "        glColor3f(1,1,0)          # amarelo",
        "        glVertex3f(-1,-1,0)",
        "        glVertex3f( 1,-1,0)",
        "        glVertex3f( 1, 1,0)",
        "        glVertex3f(-1, 1,0)",
        "        glEnd()",
        "",
        "    def desenhar_cubo(self):",
        "        glBegin(GL_QUADS)",
        "        glColor3f(0,1,1)          # ciano",
        "        for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1)]:",
        "            glVertex3f(x,y,z)",
        "        glEnd()",
        "",
        "    def desenhar_piramide(self):",
        "        glBegin(GL_TRIANGLES)",
        "        glColor3f(1,0,1)          # magenta",
        "        glVertex3f(-1,-1,0)",
        "        glVertex3f( 1,-1,0)",
        "        glVertex3f( 0, 1,0)",
        "        glEnd()",
    ],
}

_FORMAS_PYGAME = {
    "triangulo": lambda ox,oy,a: [
        (int(ox+80*math.cos(a+math.radians(90))),
         int(oy-80*math.sin(a+math.radians(90)))),
        (int(ox+80*math.cos(a+math.radians(210))),
         int(oy-80*math.sin(a+math.radians(210)))),
        (int(ox+80*math.cos(a+math.radians(330))),
         int(oy-80*math.sin(a+math.radians(330)))),
    ],
    "quadrado": lambda ox,oy,a: [
        (int(ox+70*math.cos(a+math.radians(45+i*90))),
         int(oy-70*math.sin(a+math.radians(45+i*90)))) for i in range(4)
    ],
    "piramide": lambda ox,oy,a: [
        (int(ox+80*math.cos(a+math.radians(90))),
         int(oy-80*math.sin(a+math.radians(90)))),
        (int(ox+80*math.cos(a+math.radians(210))),
         int(oy-80*math.sin(a+math.radians(210)))),
        (int(ox+80*math.cos(a+math.radians(330))),
         int(oy-80*math.sin(a+math.radians(330)))),
    ],
}
_CORES = {
    "triangulo": (100,200,100),
    "quadrado":  (220,200,60),
    "cubo":      (60,200,200),
    "piramide":  (200,60,200),
}


class ExOpenGL02(ExemploBase):
    NAME  = "Ex02 — Formas"
    COLOR = cfg.YELLOW

    def __init__(self):
        super().__init__()
        self._tabs   = TabBar(["Demonstração", "Resolução", "Teoria"])
        self._viewer = CodeViewer(_ARQUIVOS)
        self._teoria = make_teoria_doc("ex02_formas")
        self._teoria.set_tab_offset(TAB_H)
        self._mgr    = None
        self._angle  = 0.0
        self._anim   = True
        self._formas = ["triangulo","quadrado","cubo","piramide"]
        self._idx    = 0

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Formas — Estado",
            cax+10, cay+10, 300, 260, color=(80,70,20), closable=False)
        self._win_code = self._mgr.create("Ciclo de Formas",
            cax+10, cay+285, 300, 200, color=(60,40,120), closable=False)

    def reset(self): self._angle=0.0; self._anim=True; self._idx=0
    def toggle_anim(self): self._anim = not self._anim
    def handle_action(self, action):
        super().handle_action(action)
        if action == 'inc_alt': self._idx = (self._idx+1)%len(self._formas)
        elif action == 'dec_alt': self._idx = (self._idx-1)%len(self._formas)
    def update(self, dt):
        if self._anim: self._angle = (self._angle + 45*dt) % (2*math.pi)

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

        ox = drx+cx; oy = dry+cy
        forma = self._formas[self._idx]
        cor   = _CORES[forma]

        if forma == "cubo":
            # cubo 3D simulado
            off = int(30 * math.cos(self._angle))
            pts_f = [(ox-60,oy-60),(ox+60,oy-60),(ox+60,oy+60),(ox-60,oy+60)]
            pts_b = [(p[0]+off,p[1]-off) for p in pts_f]
            pygame.draw.polygon(surface, (30,160,160), pts_f)
            pygame.draw.polygon(surface, cor, pts_f, 2)
            pygame.draw.polygon(surface, (20,120,120), pts_b, 2)
            for a,b in zip(pts_f, pts_b):
                pygame.draw.line(surface, cor, a, b, 1)
        elif forma in _FORMAS_PYGAME:
            pts = _FORMAS_PYGAME[forma](ox, oy, self._angle)
            pygame.draw.polygon(surface, tuple(c//3 for c in cor), pts)
            pygame.draw.polygon(surface, cor, pts, 2)
            for pt in pts:
                pygame.draw.circle(surface, cor, pt, 5)

        fn = fonts['sm']
        lbl = fn.render(f"{forma}  [{self._idx+1}/{len(self._formas)}]  rot={math.degrees(self._angle):.0f}°",
                        True, cor)
        surface.blit(lbl, (ox-lbl.get_width()//2, oy+110))

        rows_info = [
            ("Alternando Formas",               cfg.YELLOW),
            (f"  Forma atual: {forma}",         cor),
            (f"  Indice: {self._idx}/{len(self._formas)-1}", cfg.GRAY),
            ("",                                cfg.WHITE),
            ("Ciclo circular com %:",           cfg.BLUE),
            ("  (idx+1) % total",               cfg.GRAY),
            ("",                                cfg.WHITE),
            ("Teclas PyOpenGL:",                cfg.BLUE),
            ("  Q → forma anterior",            cfg.YELLOW),
            ("  E → proxima forma",             cfg.YELLOW),
            ("[Setas L/R] Trocar forma",        cfg.YELLOW),
            ("[ESP] Animar  [R] Reset",         cfg.YELLOW),
        ]
        rows_code = [
            ("# Ciclo de formas:",              cfg.CYAN),
            ("formas = ['tri','quad','cubo','pir']", cfg.WHITE),
            ("indice = 0",                      cfg.WHITE),
            ("",                                cfg.WHITE),
            ("# Proximo (tecla E):",            (100,140,100)),
            ("indice = (indice+1) % len(formas)", cfg.WHITE),
            ("# Anterior (tecla Q):",           (100,140,100)),
            ("indice = (indice-1) % len(formas)", cfg.WHITE),
        ]

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_code: draw_rows_in_win(surf, win, rows_code)
        self._mgr.draw_managed(surface, fonts, _content)
