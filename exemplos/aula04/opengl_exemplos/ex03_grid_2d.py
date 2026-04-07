"""
============================================================
 ex03_grid_2d.py — Grid e Movimentação 2D (Projeto 03)
============================================================
"""
import pygame, math
import config as cfg
from exemplos.base  import ExemploBase
from interface.tabs import TabBar, TAB_H
from interface.janela import WindowManager, draw_rows_in_win
from interface.ui   import draw_grid, draw_axes
from exemplos.aula04.opengl_exemplos._code_viewer import CodeViewer
from exemplos.aula04.opengl_exemplos._teoria      import make_teoria_doc

_ARQUIVOS = {
    "src/exemplo.py": [
        '"""Grid 2D + movimentacao com teclado."""',
        "from OpenGL.GL   import *",
        "from OpenGL.GLUT import *",
        "from OpenGL.GLU  import *",
        "from src.renderizador import Renderizador",
        "",
        "class Exemplo:",
        "    def __init__(self):",
        "        glutInit()",
        "        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)",
        "        glutInitWindowSize(800, 600)",
        '        glutCreateWindow(b"Grid e Movimentacao")',
        "        self.inicializar()",
        "        self.renderizador = Renderizador()",
        "        self.formas = ['ponto','linha','triangulo',",
        "                       'quadrado','circulo','elipse']",
        "        self.indice_forma  = 0",
        "        self.angulo_rotacao = 0",
        "        self.pos_x = 0",
        "        self.pos_y = 0",
        "        self.grid_visivel  = True",
        "        glutDisplayFunc(self.desenhar)",
        "        glutKeyboardFunc(self.teclado)",
        "        glutSpecialFunc(self.teclado_especial)  # setas!",
        "        glutIdleFunc(self.desenhar)",
        "",
        "    def inicializar(self):",
        "        glClearColor(0,0,0,1)",
        "        glMatrixMode(GL_PROJECTION)",
        "        glLoadIdentity()",
        "        glOrtho(-400,400,-300,300,-1,1)  # projecao ortogonal 2D",
        "        glMatrixMode(GL_MODELVIEW)",
        "",
        "    def desenhar(self):",
        "        glClear(GL_COLOR_BUFFER_BIT)",
        "        glLoadIdentity()",
        "        if self.grid_visivel:",
        "            self.renderizador.desenhar_grid()",
        "        glTranslatef(self.pos_x, self.pos_y, 0)  # move objeto",
        "        glRotatef(self.angulo_rotacao, 0,0,1)    # gira objeto",
        "        forma = self.formas[self.indice_forma]",
        "        getattr(self.renderizador,'desenhar_'+forma)()",
        "        glutSwapBuffers()",
        "",
        "    def teclado(self, tecla, x, y):",
        "        if tecla == b'\\x1b': glutLeaveMainLoop()",
        "        elif tecla == b'q': self.indice_forma = (self.indice_forma-1)%len(self.formas)",
        "        elif tecla == b'e': self.indice_forma = (self.indice_forma+1)%len(self.formas)",
        "        elif tecla == b'r': self.angulo_rotacao += 10",
        "        elif tecla == b't': self.angulo_rotacao -= 10",
        "        elif tecla == b'g': self.grid_visivel = not self.grid_visivel",
        "",
        "    def teclado_especial(self, tecla, x, y):",
        "        if   tecla == GLUT_KEY_LEFT:  self.pos_x -= 10",
        "        elif tecla == GLUT_KEY_RIGHT: self.pos_x += 10",
        "        elif tecla == GLUT_KEY_UP:    self.pos_y += 10",
        "        elif tecla == GLUT_KEY_DOWN:  self.pos_y -= 10",
        "",
        "    def executar(self): glutMainLoop()",
    ],
    "src/renderizador.py": [
        "from OpenGL.GL import *",
        "import math",
        "",
        "class Renderizador:",
        "    def desenhar_grid(self):",
        "        glColor3f(0.3, 0.3, 0.3)",
        "        glBegin(GL_LINES)",
        "        for i in range(-400, 401, 50):  # linhas verticais",
        "            glVertex2f(i, -300); glVertex2f(i,  300)",
        "        for j in range(-300, 301, 50):  # linhas horizontais",
        "            glVertex2f(-400, j); glVertex2f( 400, j)",
        "        glEnd()",
        "",
        "    def desenhar_circulo(self):",
        "        glBegin(GL_POLYGON)",
        "        glColor3f(1, 1, 0)",
        "        for i in range(100):",
        "            ang = 2 * math.pi * i / 100",
        "            glVertex2f(50*math.cos(ang), 50*math.sin(ang))",
        "        glEnd()",
        "",
        "    def desenhar_elipse(self):",
        "        glBegin(GL_POLYGON)",
        "        glColor3f(0, 1, 1)",
        "        for i in range(100):",
        "            ang = 2 * math.pi * i / 100",
        "            glVertex2f(80*math.cos(ang), 50*math.sin(ang))",
        "        glEnd()",
    ],
}

_FORMAS_INFO = {
    "ponto":     ("GL_POINTS",    (255,255,255), "Ponto central na origem"),
    "linha":     ("GL_LINES",     (255,80,80),   "Linha horizontal -100 a 100"),
    "triangulo": ("GL_TRIANGLES", (80,220,80),   "Triangulo equilatero 50px"),
    "quadrado":  ("GL_QUADS",     (80,80,255),   "Quadrado 100x100"),
    "circulo":   ("GL_POLYGON",   (220,200,60),  "Circulo r=50, N=100 pts"),
    "elipse":    ("GL_POLYGON",   (60,200,200),  "Elipse a=80 b=50"),
}
_FORMAS = list(_FORMAS_INFO.keys())


class ExOpenGL03(ExemploBase):
    NAME  = "Ex03 — Grid 2D"
    COLOR = cfg.ORANGE

    def __init__(self):
        super().__init__()
        self._tabs   = TabBar(["Demonstração", "Resolução", "Teoria"])
        self._viewer = CodeViewer(_ARQUIVOS)
        self._teoria = make_teoria_doc("ex03_grid_2d")
        self._teoria.set_tab_offset(TAB_H)
        self._mgr    = None
        self._idx    = 2   # começa com triangulo
        self._px     = 0.0; self._py = 0.0
        self._ang    = 0.0
        self._anim   = True
        self._grid   = True

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Grid 2D — Estado",
            cax+10, cay+10, 300, 270, color=(100,50,10), closable=False)
        self._win_controles = self._mgr.create("Controles",
            cax+10, cay+295, 300, 190, color=(20,80,100), closable=False)

    def reset(self):
        self._px=0.0; self._py=0.0; self._ang=0.0; self._anim=True; self._idx=2
    def toggle_anim(self): self._anim = not self._anim
    def handle_action(self, action):
        if action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':     self.reset()
        elif action == 'inc':       self._py += 20
        elif action == 'dec':       self._py -= 20
        elif action == 'inc_alt':   self._px += 20
        elif action == 'dec_alt':   self._px -= 20
    def handle_extra(self, key):
        if key == pygame.K_g:   self._grid = not self._grid
        elif key == pygame.K_q: self._idx = (self._idx-1)%len(_FORMAS)
        elif key == pygame.K_e: self._idx = (self._idx+1)%len(_FORMAS)
        elif key == pygame.K_r: self._ang += 15
        elif key == pygame.K_t: self._ang -= 15
    def update(self, dt):
        if self._anim: self._ang = (self._ang + 30*dt) % 360

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

        # Grid fundo (respeitando estado)
        if self._grid:
            draw_grid(surface, cr, cx, cy, step=40, color=(25,40,55))
        draw_axes(surface, cr, cx, cy, font=fonts['sm'])

        ox = drx + cx + int(self._px * 0.25)
        oy = dry + cy - int(self._py * 0.25)
        a  = math.radians(self._ang)
        nome = _FORMAS[self._idx]
        prim, cor, desc = _FORMAS_INFO[nome]

        # Desenha a forma rotacionada
        def rot(x,y):
            rx = x*math.cos(a) - y*math.sin(a)
            ry = x*math.sin(a) + y*math.cos(a)
            return (int(ox+rx), int(oy-ry))

        if nome == "ponto":
            pygame.draw.circle(surface, cor, (ox,oy), 8)
        elif nome == "linha":
            pygame.draw.line(surface, cor, rot(-80,0), rot(80,0), 3)
        elif nome in ("triangulo","piramide"):
            pts = [rot(-50,-40), rot(50,-40), rot(0,60)]
            pygame.draw.polygon(surface, tuple(c//4 for c in cor), pts)
            pygame.draw.polygon(surface, cor, pts, 2)
        elif nome == "quadrado":
            pts = [rot(-50,-50), rot(50,-50), rot(50,50), rot(-50,50)]
            pygame.draw.polygon(surface, tuple(c//4 for c in cor), pts)
            pygame.draw.polygon(surface, cor, pts, 2)
        elif nome == "circulo":
            N = 60
            pts = [rot(int(50*math.cos(2*math.pi*i/N)),
                       int(50*math.sin(2*math.pi*i/N))) for i in range(N)]
            pygame.draw.polygon(surface, tuple(c//4 for c in cor), pts)
            pygame.draw.polygon(surface, cor, pts, 2)
        elif nome == "elipse":
            N = 60
            pts = [rot(int(80*math.cos(2*math.pi*i/N)),
                       int(50*math.sin(2*math.pi*i/N))) for i in range(N)]
            pygame.draw.polygon(surface, tuple(c//4 for c in cor), pts)
            pygame.draw.polygon(surface, cor, pts, 2)

        fn = fonts['sm']
        lbl = fn.render(f"{nome} | {prim} | {self._ang:.0f}°", True, cor)
        surface.blit(lbl, (ox-lbl.get_width()//2, oy+80))

        rows_info = [
            ("Grid 2D + Movimentacao",          cfg.ORANGE),
            (f"  Forma: {nome}",                cor),
            (f"  Primitivo: {prim}",            cfg.GRAY),
            (f"  Desc: {desc}",                 cfg.GRAY),
            (f"  Angulo: {self._ang:.0f} deg",  cfg.WHITE),
            (f"  Pos: ({self._px:.0f},{self._py:.0f})", cfg.WHITE),
            (f"  Grid: {'ON' if self._grid else 'OFF'}", cfg.GREEN if self._grid else cfg.GRAY2),
            ("",                                cfg.WHITE),
            ("glOrtho(-400,400,-300,300)",      cfg.CYAN),
            ("[ESP] Anim [R] Reset",            cfg.YELLOW),
        ]
        rows_ctrl = [
            ("Teclas (igual PyOpenGL):",        cfg.BLUE),
            ("  Setas → Mover objeto",          cfg.YELLOW),
            ("  Q/E   → Trocar forma",          cfg.YELLOW),
            ("  R/T   → Rotacionar",            cfg.YELLOW),
            ("  G     → Toggle grid",           cfg.YELLOW),
            ("",                                cfg.WHITE),
            ("glutSpecialFunc → setas",         cfg.CYAN),
            ("glutKeyboardFunc → chars",        cfg.CYAN),
        ]

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_controles: draw_rows_in_win(surf, win, rows_ctrl)
        self._mgr.draw_managed(surface, fonts, _content)
