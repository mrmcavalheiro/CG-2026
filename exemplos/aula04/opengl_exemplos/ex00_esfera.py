"""
============================================================
 exemplos/aula04/opengl_exemplos/ex00_esfera.py
 Exemplo 00 — Esfera 3D com PyOpenGL
 Demonstra: janela OpenGL, câmera perspectiva, gluSphere
============================================================
"""
import pygame
import math
import config as cfg
from exemplos.base  import ExemploBase
from interface.tabs import TabBar, TAB_H
from interface.janela import WindowManager, draw_rows_in_win
from interface.ui   import draw_grid, draw_axes, world_to_screen, draw_polygon
from exemplos.aula04.opengl_exemplos._code_viewer import CodeViewer
from exemplos.aula04.opengl_exemplos._teoria      import make_teoria_doc
from interface.doc_view import DocView

# ── Conteúdo do código-fonte (Projeto 00) ────────────────
_ARQUIVOS = {
    "run.py": [
        '"""',
        'Ponto de entrada do projeto.',
        'Instancia Exemplo e chama executar().',
        '"""',
        "",
        "from src.exemplo import Exemplo",
        "",
        'if __name__ == "__main__":',
        "    app = Exemplo()",
        "    app.executar()",
    ],
    "src/exemplo.py": [
        "from OpenGL.GL import *",
        "from OpenGL.GLUT import *",
        "from OpenGL.GLU import *",
        "from src.renderizador import Renderizador",
        "",
        "class Exemplo:",
        '    def __init__(self):',
        '        """Inicializa janela OpenGL."""',
        "        glutInit()",
        "        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)",
        "        glutInitWindowSize(800, 600)",
        '        glutCreateWindow(b"PyOpenGL - Esfera 3D")',
        "",
        "        glEnable(GL_DEPTH_TEST)       # teste de profundidade",
        "        glClearColor(0,0,0,1)         # fundo preto",
        "",
        "        self.renderizador = Renderizador()",
        "",
        "        # Configuracao da camera",
        "        glMatrixMode(GL_PROJECTION)",
        "        glLoadIdentity()",
        "        gluPerspective(45, 800/600, 1, 1000)  # FOV, aspect, near, far",
        "        gluLookAt(0,0,20, 0,0,0, 0,1,0)       # pos, alvo, up",
        "        glMatrixMode(GL_MODELVIEW)",
        "",
        "        glutDisplayFunc(self.desenhar)",
        "        glutIdleFunc(self.desenhar)",
        "        glutKeyboardFunc(self.teclado)",
        "",
        "    def desenhar(self):",
        "        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)",
        "        self.renderizador.desenhar_esfera()",
        "        glutSwapBuffers()",
        "",
        "    def teclado(self, tecla, x, y):",
        "        if tecla == b'\\x1b':  # ESC",
        "            glutLeaveMainLoop()",
        "",
        "    def executar(self):",
        "        glutMainLoop()",
    ],
    "src/renderizador.py": [
        "from OpenGL.GL import *",
        "from OpenGL.GLU import *",
        "",
        "class Renderizador:",
        "    def desenhar_esfera(self):",
        '        """Desenha uma esfera 3D usando gluSphere."""',
        "        glColor3f(0.3, 0.5, 1.0)   # cor azul",
        "        glPushMatrix()             # salva matriz",
        "",
        "        esfera = gluNewQuadric()              # cria objeto quadric",
        "        gluQuadricDrawStyle(esfera, GLU_FILL) # estilo: preenchido",
        "        gluSphere(esfera, 3, 20, 20)          # raio=3, lat=20, lon=20",
        "        gluDeleteQuadric(esfera)              # libera memoria",
        "",
        "        glPopMatrix()              # restaura matriz",
    ],
}

_CONCEITOS = [
    ("GL_DEPTH_TEST",    "Habilita o z-buffer: pixels mais proximos cobrem os mais distantes."),
    ("gluPerspective",   "Define o frustum: FOV, aspect ratio, near/far clipping planes."),
    ("gluLookAt",        "Posiciona a camera: ponto do olho, ponto alvo, vetor 'up'."),
    ("gluNewQuadric",    "Cria um objeto quadric (esfera, cilindro, cone, disco) na GLU."),
    ("gluSphere",        "Desenha esfera: raio, subdivisoes longitudinais, latitudinais."),
    ("glPushMatrix",     "Empilha a matriz atual — permite transformacoes locais sem afetar a cena."),
    ("glutSwapBuffers",  "Troca front/back buffer — elimina flickering (double buffering)."),
]


class ExOpenGL00(ExemploBase):
    NAME  = "Ex00 — Esfera 3D"
    COLOR = cfg.CYAN

    def __init__(self):
        super().__init__()
        self._tabs   = TabBar(["Demonstração", "Resolução", "Teoria"])
        self._viewer = CodeViewer(_ARQUIVOS)
        self._teoria = make_teoria_doc("ex00_esfera")
        self._teoria.set_tab_offset(TAB_H)
        self._mgr    = None
        self._angle  = 0.0
        self._anim   = True

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Esfera 3D — Conceitos",
            cax+10, cay+10, 320, 300, color=(20,80,160), closable=False)
        self._win_api  = self._mgr.create("API OpenGL Usada",
            cax+10, cay+325, 320, 240, color=(20,100,70), closable=False)

    def reset(self):
        self._angle = 0.0
        self._anim  = True

    def toggle_anim(self):
        self._anim = not self._anim

    def update(self, dt):
        if self._anim:
            self._angle = (self._angle + 40 * dt) % 360

    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 1:
            return self._viewer.handle_mouse_down(pos)
        if self._tabs.active == 2:
            return self._teoria.handle_mouse_down(pos, cfg.canvas_rect())
        if self._tabs.active == 0 and self._mgr:
            return self._mgr.handle_mouse_down(pos)
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 1:
            self._viewer.handle_mouse_move(pos)
        elif self._tabs.active == 2:
            self._teoria.handle_mouse_move(pos)
        elif self._mgr:
            self._mgr.handle_mouse_move(pos)

    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        self._viewer.handle_mouse_up()
        self._teoria.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)

    def handle_scroll(self, dy):
        if self._tabs.active == 1:
            self._viewer.handle_scroll(dy)
        elif self._tabs.active == 2:
            self._teoria.handle_scroll(dy)
        elif self._mgr:
            self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)

    def draw(self, surface, fonts):
        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        if self._tabs.active == 1:
            self._viewer.render(surface, fonts)
            return
        if self._tabs.active == 2:
            self._teoria.render(surface)
            return

        # ── Demonstração ─────────────────────────────────
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cr = (drx, dry, drw, drh)
        cx = drw // 2; cy = drh // 2

        draw_grid(surface, cr, cx, cy)
        draw_axes(surface, cr, cx, cy, font=fonts['sm'])

        # Esfera simulada em pygame — projeção perspectiva manual
        self._draw_sphere_demo(surface, fonts, drx+cx, dry+cy, drw, drh)

        rows_info = [
            ("Projeto 00 — Esfera 3D",        cfg.CYAN),
            ("",                               cfg.WHITE),
            ("Conceito central:",              cfg.BLUE),
            ("  Renderizacao 3D com OpenGL",   cfg.GRAY),
            ("  Camera perspectiva",           cfg.GRAY),
            ("  gluSphere para esfera",        cfg.GRAY),
            ("  GL_DEPTH_TEST (z-buffer)",     cfg.GRAY),
            ("",                               cfg.WHITE),
            ("Controles no PyOpenGL:",         cfg.BLUE),
            ("  ESC → fechar janela",          cfg.YELLOW),
            ("",                               cfg.WHITE),
            ("[ESP] Animar  [R] Reset",        cfg.YELLOW),
        ]
        rows_api = [
            ("Funcoes OpenGL/GLU:",            cfg.GREEN),
            ("  glutInit()",                   cfg.WHITE),
            ("  glutInitDisplayMode()",        cfg.WHITE),
            ("  gluPerspective(fov,ar,n,f)",   cfg.WHITE),
            ("  gluLookAt(eye,at,up)",         cfg.WHITE),
            ("  gluNewQuadric()",              cfg.WHITE),
            ("  gluSphere(q, r, lat, lon)",    cfg.WHITE),
            ("  glPushMatrix()",               cfg.WHITE),
            ("  glPopMatrix()",                cfg.WHITE),
            ("  glutSwapBuffers()",            cfg.WHITE),
        ]

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_api:  draw_rows_in_win(surf, win, rows_api)

        self._mgr.draw_managed(surface, fonts, _content)

    def _draw_sphere_demo(self, surface, fonts, ox, oy, drw, drh):
        """Simula visualmente uma esfera 3D rotacionando em pygame."""
        R = min(drw, drh) // 5
        # sombra
        shadow = pygame.Surface((R*2+10, R//2+6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,80), (0, 0, R*2+10, R//2+6))
        surface.blit(shadow, (ox - R - 5, oy + R - 4))

        # corpo da esfera (gradiente simulado com círculos concêntricos)
        for i in range(R, 0, -3):
            t = i / R
            r = int(40  + (1-t) * 60)
            g = int(80  + (1-t) * 80)
            b = int(200 + (1-t) * 55)
            pygame.draw.circle(surface, (r, g, b), (ox, oy), i)

        # meridianos rotacionando
        a = math.radians(self._angle)
        for i in range(8):
            ang = a + i * math.pi / 4
            # elipse para simular meridiano
            stretch = abs(math.cos(ang))
            hw = max(2, int(R * stretch))
            rect = pygame.Rect(ox - hw, oy - R, hw*2, R*2)
            if rect.width > 2:
                pygame.draw.ellipse(surface, (80, 140, 255, 100), rect, 1)

        # paralelos (linhas horizontais)
        for lat in range(-3, 4):
            py = oy + lat * R // 4
            ry = int(math.sqrt(max(0, R**2 - (lat * R//4)**2)))
            if ry > 2:
                pygame.draw.ellipse(surface, (60, 120, 200),
                                    (ox - ry, py - 3, ry*2, 6), 1)

        # contorno
        pygame.draw.circle(surface, (150, 200, 255), (ox, oy), R, 2)

        # label
        fn = fonts['sm']
        lbl = fn.render(f"gluSphere(r=3)  rot={self._angle:.0f}°", True, cfg.CYAN)
        surface.blit(lbl, (ox - lbl.get_width()//2, oy + R + 12))
