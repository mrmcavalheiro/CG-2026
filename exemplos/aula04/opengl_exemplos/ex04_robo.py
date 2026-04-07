"""
============================================================
 ex04_robo.py — Robô com Hierarquia (Projeto 04)
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
    "src/renderizador.py": [
        '"""Hierarquia de transformacoes: robo com bracos."""',
        "from OpenGL.GL import *",
        "",
        "class Renderizador:",
        "    def desenhar_robo(self, ang1, ang2, tx, ty):",
        "        glPushMatrix()              # estado global",
        "        glTranslatef(tx, ty, 0)     # move o robo",
        "        glRotatef(ang1, 0,0,1)      # gira o corpo",
        "",
        "        # Base do robo",
        "        glColor3f(0, 0, 1)",
        "        self._desenhar_base(100, 60)",
        "",
        "        # Braco 1 — gira em relacao ao corpo",
        "        glColor3f(0, 1, 0)",
        "        self._desenhar_braco(20, 40, ang1)",
        "",
        "        # Braco 2 — gira em sentido oposto",
        "        glColor3f(1, 0, 0)",
        "        self._desenhar_braco(20, 40, ang2)",
        "",
        "        glPopMatrix()              # restaura estado global",
        "",
        "    def _desenhar_base(self, larg, alt):",
        "        glBegin(GL_LINE_LOOP)      # contorno fechado",
        "        glVertex2f(-larg/3,  alt/2)",
        "        glVertex2f( larg/3,  alt/2)",
        "        glVertex2f( larg/2, -alt/2)",
        "        glVertex2f(-larg/2, -alt/2)",
        "        glEnd()",
        "",
        "    def _desenhar_braco(self, larg, alt, angulo):",
        "        glPushMatrix()             # salva estado do corpo",
        "        glRotatef(angulo, 0,0,1)   # gira o braco",
        "        glBegin(GL_LINE_LOOP)",
        "        glVertex2f(-larg/3, alt)",
        "        glVertex2f( larg/3, alt)",
        "        glVertex2f( larg/3, -alt/8)",
        "        glVertex2f(-larg/3, -alt/8)",
        "        glEnd()",
        "        glPopMatrix()              # restaura estado do corpo",
    ],
    "src/exemplo.py": [
        "from OpenGL.GLUT import *",
        "from OpenGL.GL   import glClear, GL_COLOR_BUFFER_BIT, glLoadIdentity",
        "from src.renderizador import Renderizador",
        "",
        "class Exemplo:",
        "    def __init__(self):",
        "        glutInit()",
        "        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)",
        "        glutInitWindowSize(800, 600)",
        '        glutCreateWindow(b"PyOpenGL - Robo")',
        "        self.renderizador = Renderizador()",
        "        self.transX = 0.0",
        "        self.transY = 0.0",
        "        self.angulo = 0.0",
        "        glutDisplayFunc(self.desenhar)",
        "        glutKeyboardFunc(self.teclado)",
        "        glutSpecialFunc(self.teclado_especial)",
        "",
        "    def desenhar(self):",
        "        glClear(GL_COLOR_BUFFER_BIT)",
        "        glLoadIdentity()",
        "        self.renderizador.desenhar_grid()",
        "        self.renderizador.desenhar_robo(",
        "            self.angulo, -self.angulo,",
        "            self.transX, self.transY)",
        "        glutPostRedisplay()",
        "",
        "    def teclado_especial(self, tecla, x, y):",
        "        if tecla == 100: self.transX -= 0.5   # seta esq",
        "        if tecla == 102: self.transX += 0.5   # seta dir",
        "        if tecla == 101: self.transY += 0.5   # seta cima",
        "        if tecla == 103: self.transY -= 0.5   # seta baixo",
        "        glutPostRedisplay()",
        "",
        "    def executar(self): glutMainLoop()",
    ],
    "src/camera.py": [
        "from OpenGL.GL  import *",
        "from OpenGL.GLU import *",
        "",
        "class Camera:",
        "    def __init__(self):",
        "        self.cameraZ = 800.0  # distancia da camera",
        "",
        "    def configurar(self):",
        "        glMatrixMode(GL_PROJECTION)",
        "        glLoadIdentity()",
        "        gluPerspective(45, 1.0, 1, 1000)",
        "        gluLookAt(0,0,self.cameraZ, 0,0,0, 0,1,0)",
        "        glMatrixMode(GL_MODELVIEW)",
        "        glLoadIdentity()",
    ],
}


def _draw_robo_pygame(surface, ox, oy, base_x, ang1_deg, ang2_deg, fonts):
    """
    Robô hierárquico correto:
      - Base (azul): SÓ desloca em X — NÃO rotaciona
      - Braço 1 (verde): rotaciona a partir do topo da base
      - Braço 2 (vermelho): rotaciona a partir da ponta do Braço 1
    """
    # Comprimentos dos braços
    L1 = 80   # comprimento Braço 1
    L2 = 65   # comprimento Braço 2
    BASE_W = 44
    BASE_H = 55

    a1 = math.radians(ang1_deg)
    a2 = math.radians(ang2_deg)   # relativo ao Braço 1

    # Centro da base (só X é deslocado)
    bx = ox + int(base_x)
    by = oy   # Y fixo (centro do canvas)

    # ── Base (azul) — apenas translação em X ─────────────
    base_rect_pts = [
        (bx - BASE_W//2, by - BASE_H),   # topo esq
        (bx + BASE_W//2, by - BASE_H),   # topo dir
        (bx + BASE_W//2 + 8, by),        # base dir (trapezoide)
        (bx - BASE_W//2 - 8, by),        # base esq
    ]
    pygame.draw.polygon(surface, (15, 40, 110), base_rect_pts)
    pygame.draw.polygon(surface, (80, 130, 255), base_rect_pts, 2)
    # detalhe interno
    pygame.draw.rect(surface, (30, 70, 180),
                     (bx - BASE_W//4, by - BASE_H + 6, BASE_W//2, BASE_H//3))

    # Pino da base (eixo motor do Braço 1)
    p0x, p0y = float(bx), float(by - BASE_H)
    pygame.draw.circle(surface, (60, 60, 60), (int(p0x), int(p0y)), 9)
    pygame.draw.circle(surface, (130, 130, 130), (int(p0x), int(p0y)), 5)
    pygame.draw.circle(surface, (220, 220, 220), (int(p0x), int(p0y)), 2)

    # ── Braço 1 (verde) — ancora no topo da base ─────────
    p1x = p0x + L1 * math.cos(a1)
    p1y = p0y - L1 * math.sin(a1)

    # sombra
    pygame.draw.line(surface, (0,0,0),
                     (int(p0x)+2, int(p0y)+2), (int(p1x)+2, int(p1y)+2), 14)
    # corpo
    pygame.draw.line(surface, (100, 160, 100),
                     (int(p0x), int(p0y)), (int(p1x), int(p1y)), 14)
    pygame.draw.line(surface, (150, 230, 150),
                     (int(p0x), int(p0y)), (int(p1x), int(p1y)), 5)

    # Pino da junção Braço1 → Braço 2
    pygame.draw.circle(surface, (0, 0, 0),      (int(p1x)+2, int(p1y)+2), 11)
    pygame.draw.circle(surface, (30, 80, 200),  (int(p1x), int(p1y)), 11)
    pygame.draw.circle(surface, (100, 170, 255),(int(p1x), int(p1y)), 6)
    pygame.draw.circle(surface, (220, 240, 255),(int(p1x), int(p1y)), 2)

    # ── Braço 2 (vermelho/laranja) — ancora na ponta do B1
    ang_total = a1 + a2   # ângulo absoluto = B1 + B2 relativo
    p2x = p1x + L2 * math.cos(ang_total)
    p2y = p1y - L2 * math.sin(ang_total)

    # sombra
    pygame.draw.line(surface, (0,0,0),
                     (int(p1x)+2, int(p1y)+2), (int(p2x)+2, int(p2y)+2), 12)
    # corpo
    pygame.draw.line(surface, (160, 100, 20),
                     (int(p1x), int(p1y)), (int(p2x), int(p2y)), 12)
    pygame.draw.line(surface, (240, 190, 60),
                     (int(p1x), int(p1y)), (int(p2x), int(p2y)), 4)

    # Ponta (efetuador / garra)
    pygame.draw.circle(surface, (0,0,0),       (int(p2x)+1, int(p2y)+1), 8)
    pygame.draw.circle(surface, (200, 200, 200),(int(p2x), int(p2y)), 8)
    pygame.draw.circle(surface, (255, 255, 255),(int(p2x), int(p2y)), 4)

    # ── Labels ────────────────────────────────────────────
    fn = fonts['sm']
    def lbl(txt, x, y, cor):
        s = fn.render(txt, True, cor)
        bg = pygame.Surface((s.get_width()+6, s.get_height()+2), pygame.SRCALPHA)
        bg.fill((0,0,0,140))
        surface.blit(bg, (int(x)-s.get_width()//2-3, int(y)-s.get_height()//2-1))
        surface.blit(s,  (int(x)-s.get_width()//2,   int(y)-s.get_height()//2))

    mid1x = (p0x+p1x)/2; mid1y = (p0y+p1y)/2
    mid2x = (p1x+p2x)/2; mid2y = (p1y+p2y)/2
    lbl(f"B1={ang1_deg:.0f}°", mid1x+14, mid1y, (150,230,150))
    lbl(f"B2={ang2_deg:.0f}°", mid2x+14, mid2y, (240,190,60))
    lbl(f"BaseX={base_x:.0f}", bx, by+20, (100,150,255))
    lbl(f"Garra=({int(p2x-ox)},{int(oy-p2y)})", p2x+14, p2y-12, (220,220,220))


class ExOpenGL04(ExemploBase):
    NAME  = "Ex04 — Robô"
    COLOR = cfg.RED

    def __init__(self):
        super().__init__()
        self._tabs   = TabBar(["Demonstração", "Resolução", "Teoria"])
        self._viewer = CodeViewer(_ARQUIVOS)
        self._teoria = make_teoria_doc("ex04_robo")
        self._teoria.set_tab_offset(TAB_H)
        self._mgr    = None
        self._base_x = 0.0   # base: só desloca em X
        self._ang1   = 90.0  # Braço 1 (90° = vertical)
        self._ang2   = 0.0   # Braço 2 relativo ao Braço 1
        self._anim   = True

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Hierarquia — Robo",
            cax+10, cay+10, 310, 280, color=(120,20,20), closable=False)
        self._win_code = self._mgr.create("Push/Pop Matrix",
            cax+10, cay+305, 310, 200, color=(60,40,120), closable=False)

    def reset(self): self._base_x=0.0; self._ang1=90.0; self._ang2=0.0; self._anim=True
    def toggle_anim(self): self._anim = not self._anim
    def update(self, dt):
        if self._anim: self._ang1 = (self._ang1 + 30*dt) % 360
    def handle_action(self, action):
        if action=='toggle_anim': self.toggle_anim()
        elif action=='reset':     self.reset()
        elif action=='inc_alt':   self._base_x += 15  # ← Base move X
        elif action=='dec_alt':   self._base_x -= 15  # → Base move X
    def handle_extra(self, key):
        if   key == pygame.K_a:   self._ang1 = (self._ang1 + 5) % 360
        elif key == pygame.K_d:   self._ang1 = (self._ang1 - 5) % 360
        elif key == pygame.K_w:   self._ang2 = min(150, self._ang2 + 5)
        elif key == pygame.K_s:   self._ang2 = max(-150, self._ang2 - 5)

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
        draw_grid(surface, cr, cx, cy, step=50)
        draw_axes(surface, cr, cx, cy, font=fonts['sm'])

        ox = drx+cx; oy = dry+cy
        _draw_robo_pygame(surface, ox, oy,
                          self._base_x,
                          self._ang1, self._ang2, fonts)

        rows_info = [
            ("Robo — Hierarquia Correta",        cfg.RED),
            ("",                                 cfg.WHITE),
            ("  Base (azul): so desloca X",      (80,130,255)),
            (f"  BaseX = {self._base_x:.0f} px", (80,130,255)),
            ("",                                 cfg.WHITE),
            ("  Braco 1 (verde): rotaciona",     (150,230,150)),
            (f"  ang1 = {self._ang1:.1f} graus", (150,230,150)),
            ("",                                 cfg.WHITE),
            ("  Braco 2 (amarelo): rotaciona",   (240,190,60)),
            (f"  ang2 = {self._ang2:.1f} graus (rel B1)", (240,190,60)),
            ("",                                 cfg.WHITE),
            ("[←/→] Mover base em X",           cfg.YELLOW),
            ("[A/D]  Rotac. Braco 1",            cfg.YELLOW),
            ("[W/S]  Rotac. Braco 2",            cfg.YELLOW),
            ("[ESP] Anim  [R] Reset",            cfg.YELLOW),
        ]
        rows_code = [
            ("# Base: so translacao em X",       (100,140,100)),
            ("glTranslatef(base_x, 0, 0)",       cfg.WHITE),
            ("desenhar_base()      # nao gira",  cfg.WHITE),
            ("",                                 cfg.WHITE),
            ("# Braco 1: rotacao propria",       (100,140,100)),
            ("glPushMatrix()",                   cfg.CYAN),
            ("  glRotatef(ang1, 0,0,1)",         (150,230,150)),
            ("  desenhar_braco1()",              cfg.WHITE),
            ("",                                 cfg.WHITE),
            ("  # Braco 2: relativo ao B1",      (100,140,100)),
            ("  glPushMatrix()",                 cfg.CYAN),
            ("    glRotatef(ang2, 0,0,1)",       (240,190,60)),
            ("    desenhar_braco2()",            cfg.WHITE),
            ("  glPopMatrix()",                  cfg.CYAN),
            ("glPopMatrix()",                    cfg.CYAN),
        ]

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_code: draw_rows_in_win(surf, win, rows_code)
        self._mgr.draw_managed(surface, fonts, _content)
