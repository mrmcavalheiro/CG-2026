"""
============================================================
 ex06_braco.py — Exercício 02: Braço Robótico Articulado
 Base fixa (move X) + Braço 1 + Braço 2 com pinos (eixos)
 Conforme imagem: plataforma marrom, corpo vermelho,
 braço 1 cinza com pino, braço 2 amarelo com pino.
============================================================
"""
import pygame
import math
import config as cfg
from exemplos.base  import ExemploBase
from interface.tabs import TabBar, TAB_H
from interface.janela import WindowManager, draw_rows_in_win
from interface.ui   import draw_axes
from exemplos.aula04.opengl_exemplos._code_viewer import CodeViewer
from exemplos.aula04.opengl_exemplos._teoria      import make_teoria_doc
from interface.doc_view import DOCS, _b, _h, _s, _t, _c, _li, _th, _tr, _eq, _sep, _bl

# ── Teoria ───────────────────────────────────────────────
DOCS["ex06_braco"] = [
    _t("Exercício 02 — Braço Robótico Articulado"),
    _s("Aula 04 — Computacao Grafica | UNIJUI 2026"),
    _sep(),
    _h("Objetivo"),
    _b("Desenvolver um braco robotico articulado com: base fixa (move em X),"
       " Braco 1 rotacionavel conectado a base, Braco 2 rotacionavel conectado"
       " a extremidade do Braco 1. Cada juncao tem um PINO (esfera cinza/azul)"
       " representando o eixo do motor."),
    _bl(),
    _h("Estrutura Visual (conforme imagem)"),
    _th("Parte          |  Cor       |  Funcao"),
    _tr("Plataforma     |  Marrom    |  Chao fixo"),
    _tr("Corpo/Base     |  Vermelho  |  Move no eixo X"),
    _tr("Braco 1        |  Cinza     |  Rotaciona a partir da base"),
    _tr("Pino 1 (eixo)  |  Cinza esc |  Motor Braco1 - na base"),
    _tr("Pino 2 (eixo)  |  Azul      |  Motor Braco2 - junção dos braços"),
    _tr("Braco 2        |  Amarelo   |  Rotaciona a partir da ponta do Braco1"),
    _eq("sen²(t) + cos²(t) = 1"),
    _bl(),
    _h("Hierarquia de Transformacoes"),
    _b("Cada parte herda as transformacoes da parte pai — exatamente como no OpenGL"
       " com glPushMatrix / glPopMatrix."),
    _c("# Passo 1: posicionar a base (translacao X)"),
    _c("base_x = base_x_inicial + deslocamento"),
    _c(""),
    _c("# Passo 2: extremidade do Braco 1"),
    _c("p1x = base_x + L1 * cos(ang1)"),
    _c("p1y = base_y - L1 * sin(ang1)"),
    _c(""),
    _c("# Passo 3: extremidade do Braco 2"),
    _c("p2x = p1x + L2 * cos(ang1 + ang2)"),
    _c("p2y = p1y - L2 * sin(ang1 + ang2)"),
    _b("Braco 2 usa ang1+ang2 porque seu angulo e relativo ao Braco 1."),
    _bl(),
    _h("Pino (Eixo de Motor)"),
    _b("Visualmente um circulo preenchido na juncao entre dois segmentos."
       " Representa o eixo de rotacao — como o eixo de um servo motor."),
    _c("pygame.draw.circle(surface, COR_PINO, (int(px), int(py)), RAIO_PINO)"),
    _c("pygame.draw.circle(surface, BRILHO,   (int(px), int(py)), RAIO_PINO//2)"),
    _bl(),
    _h("Controles de Teclado"),
    _th("Tecla   |  Acao"),
    _tr("← / →   |  Move a base no eixo X"),
    _tr("A / D    |  Rotaciona o Braco 1 (CCW/CW)"),
    _tr("W / S    |  Rotaciona o Braco 2 (CCW/CW)"),
    _tr("R        |  Reset posicao"),
    _tr("ESC      |  Sair"),
    _bl(),
    _h("Eixos de Referencia"),
    _b("O sistema exibe eixos X (laranja) e Y (verde) para referencia espacial,"
       " com setas nas extremidades positivas."),
    _c("draw_axes(surface, canvas_rect, cx, cy, font=fonts['sm'])"),
]

# ── Código-fonte ─────────────────────────────────────────
_ARQUIVOS_BRACO = {
    "braco_robotico.py": [
        '"""',
        'Braco Robotico Articulado — Exercicio 02',
        'Base (vermelho) + Braco1 (cinza) + Braco2 (amarelo)',
        'Pinos nos eixos de rotacao.',
        '"""',
        "import pygame, math",
        "from pygame.locals import *",
        "",
        "# Janela",
        "LARGURA, ALTURA = 1000, 600",
        "FPS = 60",
        "",
        "# Dimensoes",
        "BASE_W, BASE_H = 80, 120   # corpo vermelho",
        "L1 = 200                   # comprimento Braco 1",
        "L2 = 160                   # comprimento Braco 2",
        "PLATAFORMA_H = 40          # altura da plataforma marrom",
        "PINO_R = 10                # raio do pino (eixo motor)",
        "",
        "# Cores",
        "C_PLATAFORMA = (160,  82,  45)",
        "C_BASE       = (220,  40,  40)",
        "C_BRACO1     = (170, 170, 170)",
        "C_BRACO2     = (220, 190,  50)",
        "C_PINO1      = ( 80,  80,  80)",
        "C_PINO2      = ( 50, 100, 230)",
        "C_EIXO_X     = (255, 140,  30)",
        "C_EIXO_Y     = ( 60, 210,  60)",
        "",
        "class BracoRobotico:",
        "    def __init__(self):",
        "        self.base_x  = LARGURA // 2",
        "        self.base_y  = ALTURA - PLATAFORMA_H",
        "        self.ang1    = math.pi / 2   # 90 graus (vertical)",
        "        self.ang2    = 0.0           # relativo ao braco1",
        "",
        "    def atualizar(self, teclas):",
        "        passo = 3",
        "        if teclas[K_LEFT]:  self.base_x -= passo",
        "        if teclas[K_RIGHT]: self.base_x += passo",
        "        if teclas[K_a]:     self.ang1 += math.radians(2)",
        "        if teclas[K_d]:     self.ang1 -= math.radians(2)",
        "        if teclas[K_w]:     self.ang2 += math.radians(2)",
        "        if teclas[K_s]:     self.ang2 -= math.radians(2)",
        "        # Limites",
        "        self.base_x = max(BASE_W//2+10, min(LARGURA-BASE_W//2-10, self.base_x))",
        "        self.ang1   = max(math.radians(10), min(math.radians(170), self.ang1))",
        "        self.ang2   = max(math.radians(-150), min(math.radians(150), self.ang2))",
        "",
        "    def _segmento(self, surf, p1, p2, cor, esp=12):",
        "        pygame.draw.line(surf, cor, (int(p1[0]),int(p1[1])),",
        "                                    (int(p2[0]),int(p2[1])), esp)",
        "",
        "    def _pino(self, surf, pos, cor, brilho):",
        "        pygame.draw.circle(surf, cor,    (int(pos[0]),int(pos[1])), PINO_R)",
        "        pygame.draw.circle(surf, brilho, (int(pos[0]),int(pos[1])), PINO_R//2)",
        "",
        "    def desenhar(self, surf, font):",
        "        # Plataforma",
        "        pygame.draw.rect(surf, C_PLATAFORMA,",
        "            (0, ALTURA-PLATAFORMA_H, LARGURA, PLATAFORMA_H))",
        "",
        "        # Base (corpo vermelho)",
        "        bx = self.base_x; by = self.base_y",
        "        pygame.draw.rect(surf, C_BASE,",
        "            (bx-BASE_W//2, by-BASE_H, BASE_W, BASE_H))",
        "",
        "        # Juncao base -> Braco1 (pino 1 — cinza escuro)",
        "        p0 = (bx, by - BASE_H)   # topo da base",
        "",
        "        # Extremidade do Braco 1",
        "        p1 = (p0[0] + L1*math.cos(self.ang1),",
        "              p0[1] - L1*math.sin(self.ang1))",
        "",
        "        # Braco 1",
        "        self._segmento(surf, p0, p1, C_BRACO1, 14)",
        "        self._pino(surf, p0, C_PINO1, (160,160,160))",
        "",
        "        # Extremidade do Braco 2",
        "        ang_total = self.ang1 + self.ang2",
        "        p2 = (p1[0] + L2*math.cos(ang_total),",
        "              p1[1] - L2*math.sin(ang_total))",
        "",
        "        # Braco 2",
        "        self._segmento(surf, p1, p2, C_BRACO2, 12)",
        "        self._pino(surf, p1, C_PINO2, (150,190,255))",
        "",
        "        # Ponta (garra/ferramenta simulada)",
        "        pygame.draw.circle(surf, (200,200,200), (int(p2[0]),int(p2[1])), 8)",
        "        pygame.draw.circle(surf, (255,255,255), (int(p2[0]),int(p2[1])), 4)",
        "",
        "        # Eixos de coordenadas",
        "        cx, cy = LARGURA//2, ALTURA//2",
        "        pygame.draw.line(surf, C_EIXO_X, (cx-200,cy), (cx+200,cy), 2)",
        "        pygame.draw.line(surf, C_EIXO_Y, (cx,cy+150), (cx,cy-150), 2)",
        "",
        "        # Labels",
        "        a1_deg = math.degrees(self.ang1)",
        "        a2_deg = math.degrees(self.ang2)",
        "        txt = font.render(",
        "            f'Braco1={a1_deg:.0f}  Braco2={a2_deg:.0f}  BaseX={bx:.0f}',",
        "            True, (200,210,230))",
        "        surf.blit(txt, (10, 10))",
        "",
        "def main():",
        "    pygame.init()",
        "    tela = pygame.display.set_mode((LARGURA, ALTURA))",
        '    pygame.display.set_caption("Braco Robotico")',
        "    clock = pygame.time.Clock()",
        "    font  = pygame.font.SysFont('segoeui', 14)",
        "    robo  = BracoRobotico()",
        "",
        "    while True:",
        "        for ev in pygame.event.get():",
        "            if ev.type == QUIT: return",
        "            if ev.type == KEYDOWN and ev.key == K_ESCAPE: return",
        "            if ev.type == KEYDOWN and ev.key == K_r: robo.__init__()",
        "        teclas = pygame.key.get_pressed()",
        "        robo.atualizar(teclas)",
        "        tela.fill((15, 20, 35))",
        "        robo.desenhar(tela, font)",
        "        pygame.display.flip()",
        "        clock.tick(FPS)",
        "",
        "if __name__ == '__main__':",
        "    main()",
    ],
}

# ── Constantes visuais ────────────────────────────────────
_BASE_W   = 60
_BASE_H   = 90
_L1       = 160   # comprimento braço 1
_L2       = 130   # comprimento braço 2
_PLAT_H   = 30
_PINO_R   = 9

_C_PLAT   = (160, 82,  45)
_C_BASE   = (220, 40,  40)
_C_BR1    = (170,170,170)
_C_BR2    = (210,180, 40)
_C_PINO1  = ( 80, 80, 80)
_C_PINO2  = ( 50,100,230)


class ExOpenGL06(ExemploBase):
    NAME  = "Ex06 — Braço"
    COLOR = (220, 40, 40)

    def __init__(self):
        super().__init__()
        self._tabs    = TabBar(["Demonstração", "Resolução", "Teoria"])
        self._viewer  = CodeViewer(_ARQUIVOS_BRACO)
        self._teoria  = make_teoria_doc("ex06_braco")
        self._teoria.set_tab_offset(TAB_H)
        self._mgr     = None
        self._reset_state()

    def _reset_state(self):
        self._base_dx = 0.0          # deslocamento X da base
        self._ang1    = math.pi/2    # braço 1 (90°)
        self._ang2    = 0.0          # braço 2 relativo ao 1

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Braço — Estado",
            cax+10, cay+10, 290, 280, color=(80,20,20), closable=False)
        self._win_ctrl = self._mgr.create("Controles",
            cax+10, cay+305, 290, 220, color=(20,60,100), closable=False)

    def reset(self): self._reset_state()
    def update(self, dt): pass   # controlado por teclas em handle_extra

    def handle_extra(self, key):
        step_px  = 12
        step_ang = math.radians(3)
        if   key == pygame.K_LEFT:  self._base_dx -= step_px
        elif key == pygame.K_RIGHT: self._base_dx += step_px
        elif key == pygame.K_a:     self._ang1    += step_ang
        elif key == pygame.K_d:     self._ang1    -= step_ang
        elif key == pygame.K_w:     self._ang2    += step_ang
        elif key == pygame.K_s:     self._ang2    -= step_ang
        # limites
        self._ang1 = max(math.radians(10), min(math.radians(170), self._ang1))
        self._ang2 = max(math.radians(-150), min(math.radians(150), self._ang2))

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

    # ── Draw ─────────────────────────────────────────────────
    def draw(self, surface, fonts):
        if self._mgr is None: self._init_windows()
        self._tabs.draw(surface, fonts)
        if self._tabs.active == 1: self._viewer.render(surface, fonts); return
        if self._tabs.active == 2: self._teoria.render(surface); return

        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cr  = (drx, dry, drw, drh)

        # ── Eixos de referência ───────────────────────────
        cx = drw // 2
        cy = drh // 2
        draw_axes(surface, cr, cx, cy, font=fonts['sm'])

        # ── Plataforma (chão) ────────────────────────────
        plat_y = dry + drh - _PLAT_H
        pygame.draw.rect(surface, _C_PLAT, (drx, plat_y, drw, _PLAT_H))
        # Textura da plataforma (linhas)
        for xi in range(drx, drx+drw, 20):
            pygame.draw.line(surface, tuple(c-20 for c in _C_PLAT),
                             (xi, plat_y), (xi+15, plat_y+_PLAT_H), 1)

        # ── Posição da base ───────────────────────────────
        base_cx = drx + drw//2 + int(self._base_dx)
        base_cx = max(drx + _BASE_W//2 + 10,
                      min(drx + drw - _BASE_W//2 - 10, base_cx))
        base_y  = plat_y  # topo da plataforma

        # ── Base (corpo vermelho) ────────────────────────
        bx = base_cx - _BASE_W//2
        by = base_y  - _BASE_H
        pygame.draw.rect(surface, _C_BASE, (bx, by, _BASE_W, _BASE_H))
        pygame.draw.rect(surface, (255,80,80), (bx, by, _BASE_W, _BASE_H), 2)
        # destaque
        pygame.draw.rect(surface, (255,120,120), (bx+4, by+4, 8, _BASE_H-8))

        # ── Ponto de ancoragem do Braço 1 (topo da base) ─
        p0x = float(base_cx)
        p0y = float(by)  # topo da base

        # ── Extremidade do Braço 1 ────────────────────────
        p1x = p0x + _L1 * math.cos(self._ang1)
        p1y = p0y - _L1 * math.sin(self._ang1)

        # ── Extremidade do Braço 2 ────────────────────────
        ang_total = self._ang1 + self._ang2
        p2x = p1x + _L2 * math.cos(ang_total)
        p2y = p1y - _L2 * math.sin(ang_total)

        # ── Braço 1 (cinza) ───────────────────────────────
        self._desenhar_braco(surface, p0x, p0y, p1x, p1y, _C_BR1, 14)

        # ── Pino 1 (eixo na base) ─────────────────────────
        self._desenhar_pino(surface, p0x, p0y, _C_PINO1, (140,140,140), _PINO_R)

        # ── Braço 2 (amarelo) ─────────────────────────────
        self._desenhar_braco(surface, p1x, p1y, p2x, p2y, _C_BR2, 12)

        # ── Pino 2 (eixo na junção dos braços) ────────────
        self._desenhar_pino(surface, p1x, p1y, _C_PINO2, (150,190,255), _PINO_R)

        # ── Ponta (garra) ─────────────────────────────────
        pygame.draw.circle(surface, (200,200,200), (int(p2x),int(p2y)), 7)
        pygame.draw.circle(surface, (255,255,255), (int(p2x),int(p2y)), 3)

        # ── Labels nos braços ─────────────────────────────
        fn = fonts['sm']
        mid1x = int((p0x+p1x)/2); mid1y = int((p0y+p1y)/2)
        mid2x = int((p1x+p2x)/2); mid2y = int((p1y+p2y)/2)
        self._label(surface, fn, f"B1 {math.degrees(self._ang1):.0f}°", mid1x, mid1y, _C_BR1)
        self._label(surface, fn, f"B2 {math.degrees(self._ang2):.0f}°", mid2x, mid2y, _C_BR2)

        # Coordenada da garra
        garra_txt = fn.render(
            f"Garra: ({int(p2x-drx-drw//2)}, {int(drh//2-(p2y-dry))})",
            True, (180,200,230))
        surface.blit(garra_txt, (drx+drw//2 - garra_txt.get_width()//2, dry+8))

        # ── Janelas flutuantes ────────────────────────────
        rows_info = [
            ("Braço Robótico",                  (220,40,40)),
            ("",                                cfg.WHITE),
            ("Hierarquia:",                     cfg.BLUE),
            ("  Base → Braço1 → Braço2",        cfg.GRAY),
            ("",                                cfg.WHITE),
            (f"  base_dx = {self._base_dx:.0f}px", cfg.WHITE),
            (f"  ang1 = {math.degrees(self._ang1):.1f}°", _C_BR1),
            (f"  ang2 = {math.degrees(self._ang2):.1f}°", _C_BR2),
            (f"  ang_total = {math.degrees(self._ang1+self._ang2):.1f}°", cfg.CYAN),
            ("",                                cfg.WHITE),
            ("p1 = base + L1*cos(ang1)",        cfg.GRAY),
            ("p2 = p1  + L2*cos(ang1+ang2)",    cfg.GRAY),
        ]
        rows_ctrl = [
            ("Controles:",                      cfg.BLUE),
            ("  ← / →    mover base",           cfg.YELLOW),
            ("  A / D    rotac. Braço 1",       _C_BR1),
            ("  W / S    rotac. Braço 2",       _C_BR2),
            ("  R        reset",                cfg.YELLOW),
            ("",                                cfg.WHITE),
            ("Pinos (eixos de motor):",         cfg.BLUE),
            ("  ● cinza  = motor Braço 1",      _C_PINO1),
            ("  ● azul   = motor Braço 2",      _C_PINO2),
        ]

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_ctrl: draw_rows_in_win(surf, win, rows_ctrl)
        self._mgr.draw_managed(surface, fonts, _content)

    # ── Helpers de desenho ───────────────────────────────────
    def _desenhar_braco(self, surface, x1, y1, x2, y2, cor, espessura):
        """Desenha segmento do braço com sombra e brilho."""
        ix1,iy1,ix2,iy2 = int(x1),int(y1),int(x2),int(y2)
        # sombra
        pygame.draw.line(surface, (0,0,0), (ix1+2,iy1+2), (ix2+2,iy2+2), espessura+2)
        # corpo
        pygame.draw.line(surface, cor, (ix1,iy1), (ix2,iy2), espessura)
        # brilho (linha clara ao longo)
        brilho = tuple(min(255, c+60) for c in cor)
        pygame.draw.line(surface, brilho, (ix1,iy1), (ix2,iy2), max(2, espessura//4))

    def _desenhar_pino(self, surface, px, py, cor_ext, cor_int, raio):
        """Desenha pino (eixo motor) com aparência metálica."""
        ipx, ipy = int(px), int(py)
        # sombra
        pygame.draw.circle(surface, (0,0,0), (ipx+2, ipy+2), raio)
        # anel externo (mais escuro)
        cor_escura = tuple(max(0, c-40) for c in cor_ext)
        pygame.draw.circle(surface, cor_escura, (ipx,ipy), raio+2)
        # corpo
        pygame.draw.circle(surface, cor_ext, (ipx,ipy), raio)
        # núcleo (brilho)
        pygame.draw.circle(surface, cor_int, (ipx,ipy), raio//2)
        # ponto central branco
        pygame.draw.circle(surface, (255,255,255), (ipx,ipy), 2)

    def _label(self, surface, font, txt, x, y, cor):
        """Label com fundo semi-transparente."""
        s = font.render(txt, True, cor)
        bg = pygame.Surface((s.get_width()+6, s.get_height()+2), pygame.SRCALPHA)
        bg.fill((0,0,0,120))
        surface.blit(bg, (x-s.get_width()//2-3, y-s.get_height()//2-1))
        surface.blit(s,  (x-s.get_width()//2,   y-s.get_height()//2))
