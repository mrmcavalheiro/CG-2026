"""
============================================================
 ex05_relogio.py — Exercício 01: Relógio Analógico
 Sincronizado com o relógio do sistema.
 Ponteiros: vermelho=segundos, azul=minutos, verde=horas
 Desafio: números 1–12, ponteiro de alarme via teclado
============================================================
"""
import pygame
import math
import time
import config as cfg
from exemplos.base  import ExemploBase
from interface.tabs import TabBar, TAB_H
from interface.janela import WindowManager, draw_rows_in_win
from exemplos.aula04.opengl_exemplos._code_viewer import CodeViewer
from exemplos.aula04.opengl_exemplos._teoria      import make_teoria_doc
from interface.doc_view import DOCS, _b, _h, _s, _t, _c, _li, _th, _tr, _eq, _sep, _bl

# ── Teoria do exercício ───────────────────────────────────
DOCS["ex05_relogio"] = [
    _t("Exercício 01 — Relógio Analógico"),
    _s("Aula 04 — Computacao Grafica | UNIJUI 2026"),
    _sep(),
    _h("Objetivo"),
    _b("Desenvolver um relogio analogico 2D sincronizado com o horario do sistema."
       " Ponteiros em cores diferentes (vermelho=segundos, azul=minutos, verde=horas)."
       " Anel externo, numeros de 1 a 12 e ponteiro de alarme ajustavel."),
    _bl(),
    _h("Conceitos Aplicados"),
    _li("Funcoes trigonometricas para calcular a posicao dos ponteiros"),
    _li("time.localtime() para obter hora, minuto e segundo do sistema"),
    _li("Arco com pygame.draw.arc para o anel externo"),
    _li("Ponteiro de alarme controlado pelo usuario via teclado"),
    _bl(),
    _h("Calculo dos Angulos dos Ponteiros"),
    _b("O relogio comeca em 12h (topo) e gira no sentido horario."
       " Em matematica, angulo 0 e a direita e cresce anti-horario."
       " Por isso subtraimos de 90 graus (pi/2 radianos)."),
    _c("# Angulo em radianos, origem no topo, sentido horario:"),
    _c("ang_seg  = 2*pi/60  * seg  - pi/2"),
    _c("ang_min  = 2*pi/60  * min  - pi/2"),
    _c("ang_hora = 2*pi/12  * hora - pi/2"),
    _c(""),
    _c("# Adiciona fracao para movimento suave:"),
    _c("ang_min  += 2*pi/3600  * seg"),
    _c("ang_hora += 2*pi/43200 * min*60+seg"),
    _bl(),
    _h("Coordenadas do Ponteiro"),
    _c("x_ponta = cx + comprimento * math.cos(angulo)"),
    _c("y_ponta = cy + comprimento * math.sin(angulo)"),
    _li("cx, cy = centro do relogio na tela"),
    _li("comprimento = fracao do raio (seg=0.85, min=0.75, hora=0.55)"),
    _bl(),
    _h("Numeros ao Redor do Relogio (1 a 12)"),
    _c("for n in range(1, 13):"),
    _c("    ang = n * (2*pi/12) - pi/2"),
    _c("    nx  = cx + raio_num * math.cos(ang)"),
    _c("    ny  = cy + raio_num * math.sin(ang)"),
    _c("    texto = font.render(str(n), True, COR)"),
    _c("    surface.blit(texto, (nx - texto.w//2, ny - texto.h//2))"),
    _bl(),
    _h("Desafio Extra — Ponteiro de Alarme"),
    _c("# Incrementar/decrementar alarme com teclas:"),
    _c("if key == K_UP:   alarme_min = (alarme_min + 1) % 60"),
    _c("if key == K_DOWN: alarme_min = (alarme_min - 1) % 60"),
    _c("if key == K_LEFT: alarme_hora = (alarme_hora - 1) % 12"),
    _c("if key == K_RIGHT:alarme_hora = (alarme_hora + 1) % 12"),
    _bl(),
    _h("Funcao time.localtime()"),
    _th("Campo     |  Acesso            |  Descricao"),
    _tr("horas     |  t.tm_hour % 12    |  0 a 11 (formato 12h)"),
    _tr("minutos   |  t.tm_min          |  0 a 59"),
    _tr("segundos  |  t.tm_sec          |  0 a 59"),
    _eq("sen²(t) + cos²(t) = 1"),
    _bl(),
    _h("Recursos Utilizados"),
    _li("pygame.draw.line → ponteiros e marcacoes"),
    _li("pygame.draw.circle → mostrador, centro, pinos"),
    _li("pygame.draw.arc → anel externo com espessura"),
    _li("pygame.font.render → numeros 1 a 12"),
    _li("time.localtime() → hora do sistema"),
    _li("math.cos/sin → posicao dos ponteiros"),
]

# ── Código-fonte exibido na aba Resolução ─────────────────
_ARQUIVOS_RELOGIO = {
    "relogio.py": [
        '"""',
        'Relogio Analogico — Exercicio 01',
        'PyGame + time.localtime() + math.sin/cos',
        '"""',
        "import pygame, math, time",
        "from pygame.locals import *",
        "",
        "# Configuracoes",
        "LARGURA, ALTURA = 640, 640",
        "CX, CY = LARGURA//2, ALTURA//2",
        "RAIO   = 240",
        "FPS    = 60",
        "",
        "# Cores",
        "FUNDO    = (15,  20,  35)",
        "ANEL     = (200, 210, 230)",
        "MARC     = (180, 190, 210)",
        "C_SEG    = (255,  60,  60)   # vermelho",
        "C_MIN    = ( 60, 120, 255)   # azul",
        "C_HORA   = ( 60, 200,  60)   # verde",
        "C_ALARM  = (255, 200,   0)   # amarelo",
        "C_NUM    = (220, 230, 255)",
        "",
        "def ang_ponteiro(valor, total, raio_frac, extra=0):",
        '    """Angulo em rad (topo=0, sentido horario)."""',
        "    return 2*math.pi * (valor+extra)/total - math.pi/2",
        "",
        "def ponteiro(surf, cx,cy, ang, comp, cor, espessura=3):",
        '    """Desenha um ponteiro do relogio."""',
        "    x = cx + comp * math.cos(ang)",
        "    y = cy + comp * math.sin(ang)",
        "    pygame.draw.line(surf, cor, (cx,cy), (int(x),int(y)), espessura)",
        "",
        "def main():",
        "    pygame.init()",
        "    tela = pygame.display.set_mode((LARGURA, ALTURA))",
        '    pygame.display.set_caption("Relogio Analogico")',
        "    clock  = pygame.time.Clock()",
        "    fn_num = pygame.font.SysFont('segoeui', 22, bold=True)",
        "    fn_al  = pygame.font.SysFont('segoeui', 16)",
        "",
        "    alarm_h, alarm_m = 12, 0    # alarme inicial",
        "    show_alarm = True",
        "",
        "    while True:",
        "        for ev in pygame.event.get():",
        "            if ev.type == QUIT: return",
        "            if ev.type == KEYDOWN:",
        "                if ev.key == K_ESCAPE: return",
        "                if ev.key == K_UP:    alarm_m=(alarm_m+1)%60",
        "                if ev.key == K_DOWN:  alarm_m=(alarm_m-1)%60",
        "                if ev.key == K_LEFT:  alarm_h=(alarm_h-1)%12",
        "                if ev.key == K_RIGHT: alarm_h=(alarm_h+1)%12",
        "                if ev.key == K_a:     show_alarm=not show_alarm",
        "",
        "        t   = time.localtime()",
        "        seg = t.tm_sec",
        "        mnt = t.tm_min",
        "        hor = t.tm_hour % 12",
        "",
        "        tela.fill(FUNDO)",
        "",
        "        # Anel externo (triplo para espessura)",
        "        for r in range(RAIO-4, RAIO+4):",
        "            pygame.draw.circle(tela, ANEL, (CX,CY), r, 1)",
        "",
        "        # Mostrador interno",
        "        pygame.draw.circle(tela, (25,35,55), (CX,CY), RAIO-5)",
        "",
        "        # Marcacoes (horas e minutos)",
        "        for i in range(60):",
        "            a = 2*math.pi*i/60 - math.pi/2",
        "            r1 = RAIO-8  if i%5==0 else RAIO-4",
        "            r2 = RAIO-20 if i%5==0 else RAIO-12",
        "            esp = 3 if i%5==0 else 1",
        "            x1 = CX+r1*math.cos(a); y1 = CY+r1*math.sin(a)",
        "            x2 = CX+r2*math.cos(a); y2 = CY+r2*math.sin(a)",
        "            pygame.draw.line(tela, MARC, (int(x1),int(y1)), (int(x2),int(y2)), esp)",
        "",
        "        # Numeros 1 a 12",
        "        r_num = RAIO - 38",
        "        for n in range(1, 13):",
        "            a = n * (2*math.pi/12) - math.pi/2",
        "            nx = int(CX + r_num*math.cos(a))",
        "            ny = int(CY + r_num*math.sin(a))",
        "            img = fn_num.render(str(n), True, C_NUM)",
        "            tela.blit(img, (nx - img.get_width()//2, ny - img.get_height()//2))",
        "",
        "        # Alarme",
        "        if show_alarm:",
        "            a_al = ang_ponteiro(alarm_h + alarm_m/60, 12, 0)",
        "            ponteiro(tela, CX,CY, a_al, RAIO*0.65, C_ALARM, 2)",
        "",
        "        # Horas (smooth: inclui fracao de minutos)",
        "        a_h = ang_ponteiro(hor + mnt/60, 12, 0)",
        "        ponteiro(tela, CX,CY, a_h, RAIO*0.50, C_HORA, 8)",
        "",
        "        # Minutos (smooth: inclui fracao de segundos)",
        "        a_m = ang_ponteiro(mnt + seg/60, 60, 0)",
        "        ponteiro(tela, CX,CY, a_m, RAIO*0.75, C_MIN, 5)",
        "",
        "        # Segundos",
        "        a_s = ang_ponteiro(seg, 60, 0)",
        "        ponteiro(tela, CX,CY, a_s, RAIO*0.87, C_SEG, 2)",
        "        # Rabinho do ponteiro de segundos",
        "        x_r = CX - RAIO*0.12*math.cos(a_s)",
        "        y_r = CY - RAIO*0.12*math.sin(a_s)",
        "        pygame.draw.line(tela, C_SEG, (CX,CY), (int(x_r),int(y_r)), 3)",
        "",
        "        # Centro",
        "        pygame.draw.circle(tela, (230,230,230), (CX,CY), 9)",
        "        pygame.draw.circle(tela, C_SEG, (CX,CY), 5)",
        "",
        "        # HUD alarme",
        "        al_txt = f'ALARME: {alarm_h:02d}:{alarm_m:02d}  [Setas] ajustar  [A] toggle'",
        "        img = fn_al.render(al_txt, True, C_ALARM if show_alarm else (100,100,100))",
        "        tela.blit(img, (LARGURA//2 - img.get_width()//2, 10))",
        "",
        "        pygame.display.flip()",
        "        clock.tick(FPS)",
        "",
        "if __name__ == '__main__':",
        "    main()",
    ],
}


class ExOpenGL05(ExemploBase):
    NAME  = "Ex05 — Relógio"
    COLOR = (80, 160, 255)

    def __init__(self):
        super().__init__()
        self._tabs   = TabBar(["Demonstração", "Resolução", "Teoria"])
        self._viewer = CodeViewer(_ARQUIVOS_RELOGIO)
        self._teoria = make_teoria_doc("ex05_relogio")
        self._teoria.set_tab_offset(TAB_H)
        self._mgr    = None
        # Alarme ajustável
        self._alarm_h = 12
        self._alarm_m = 0
        self._show_alarm = True
        self._font_num = None

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Relógio — Info",
            cax+10, cay+10, 280, 310, color=(20,60,130), closable=False)
        self._win_ctrl = self._mgr.create("Controles",
            cax+10, cay+335, 280, 170, color=(60,40,120), closable=False)

    def reset(self):
        self._alarm_h = 12; self._alarm_m = 0; self._show_alarm = True

    def handle_action(self, action):
        if action == 'reset': self.reset()

    def handle_extra(self, key):
        if key == pygame.K_UP:    self._alarm_m = (self._alarm_m + 1) % 60
        elif key == pygame.K_DOWN:  self._alarm_m = (self._alarm_m - 1) % 60
        elif key == pygame.K_LEFT:  self._alarm_h = (self._alarm_h - 1) % 12
        elif key == pygame.K_RIGHT: self._alarm_h = (self._alarm_h + 1) % 12
        elif key == pygame.K_a:     self._show_alarm = not self._show_alarm

    def update(self, dt): pass  # usa hora real

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

        # ── Hora real do sistema ──────────────────────────
        t   = time.localtime()
        seg = t.tm_sec
        mnt = t.tm_min
        hor = t.tm_hour % 12

        # Centro do relógio na área de desenho
        cx = drx + drw // 2
        cy = dry + drh // 2
        raio = int(min(drw, drh) * 0.38)

        self._draw_clock(surface, fonts, cx, cy, raio, hor, mnt, seg)

        # Janelas flutuantes
        rows_info = [
            ("Relógio Analógico",               (150, 200, 255)),
            ("",                                cfg.WHITE),
            (f"  {t.tm_hour:02d}:{mnt:02d}:{seg:02d}", cfg.WHITE),
            ("",                                cfg.WHITE),
            ("Ponteiros:",                      cfg.BLUE),
            ("  Horas  → verde  (longo)",       (60, 200, 60)),
            ("  Minutos → azul  (médio)",       (80, 140, 255)),
            ("  Segundos → vermelho (fino)",    (255, 80, 80)),
            ("  Alarme  → amarelo",             (255, 200, 0)),
            ("",                                cfg.WHITE),
            (f"  Alarme: {self._alarm_h:02d}:{self._alarm_m:02d}", (255,200,0)),
            (f"  Status: {'ON' if self._show_alarm else 'OFF'}",
             cfg.GREEN if self._show_alarm else cfg.GRAY2),
        ]
        rows_ctrl = [
            ("Teclas de Controle:",             cfg.BLUE),
            ("  ↑/↓  → min alarme +/-",        cfg.YELLOW),
            ("  ←/→  → hora alarme +/-",       cfg.YELLOW),
            ("  A    → toggle alarme",          cfg.YELLOW),
            ("  R    → reset alarme",           cfg.YELLOW),
            ("",                                cfg.WHITE),
            ("time.localtime() → hora sistema", cfg.CYAN),
        ]

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_ctrl: draw_rows_in_win(surf, win, rows_ctrl)
        self._mgr.draw_managed(surface, fonts, _content)

    def _ang(self, valor, total):
        """Ângulo em radianos: origem no topo, sentido horário."""
        return 2 * math.pi * valor / total - math.pi / 2

    def _ponteiro(self, surface, cx, cy, ang, comp, cor, espessura):
        x = cx + comp * math.cos(ang)
        y = cy + comp * math.sin(ang)
        pygame.draw.line(surface, cor, (cx, cy), (int(x), int(y)), espessura)

    def _draw_clock(self, surface, fonts, cx, cy, raio, hor, mnt, seg):
        # ── Sombra ───────────────────────────────────────
        shadow = pygame.Surface((raio*2+20, raio*2+20), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0,0,0,60), (raio+10, raio+10), raio+10)
        surface.blit(shadow, (cx-raio-10, cy-raio-10))

        # ── Anel externo (3 camadas de espessura) ────────
        for dr in range(-4, 5):
            lum = 200 - abs(dr)*15
            pygame.draw.circle(surface, (lum,lum+10,lum+20),
                               (cx, cy), raio+dr, 1)

        # ── Fundo do mostrador ───────────────────────────
        pygame.draw.circle(surface, (18, 26, 48), (cx, cy), raio - 5)

        # ── Marcações de minutos e horas ─────────────────
        for i in range(60):
            a  = self._ang(i, 60)
            if i % 5 == 0:   # marcação de hora
                r1, r2, esp = raio-8, raio-24, 3
                cor_m = (200, 210, 230)
            else:             # marcação de minuto
                r1, r2, esp = raio-8, raio-14, 1
                cor_m = (80, 100, 130)
            x1 = cx + r1*math.cos(a); y1 = cy + r1*math.sin(a)
            x2 = cx + r2*math.cos(a); y2 = cy + r2*math.sin(a)
            pygame.draw.line(surface, cor_m,
                             (int(x1),int(y1)), (int(x2),int(y2)), esp)

        # ── Números 1 a 12 ───────────────────────────────
        if self._font_num is None:
            self._font_num = pygame.font.SysFont("segoeui", max(12, raio//12), bold=True)
        r_num = raio - max(34, raio//6)
        for n in range(1, 13):
            a  = self._ang(n, 12)
            nx = int(cx + r_num * math.cos(a))
            ny = int(cy + r_num * math.sin(a))
            img = self._font_num.render(str(n), True, (210, 220, 240))
            surface.blit(img, (nx - img.get_width()//2, ny - img.get_height()//2))

        # ── Ponteiro de alarme ───────────────────────────
        if self._show_alarm:
            a_al = self._ang(self._alarm_h + self._alarm_m / 60, 12)
            # linha tracejada
            comp_al = raio * 0.65
            for i in range(0, int(comp_al), 8):
                x1 = cx + i * math.cos(a_al)
                y1 = cy + i * math.sin(a_al)
                x2 = cx + min(i+5, comp_al) * math.cos(a_al)
                y2 = cy + min(i+5, comp_al) * math.sin(a_al)
                pygame.draw.line(surface, (255,200,0),
                                 (int(x1),int(y1)), (int(x2),int(y2)), 2)
            # diamante na ponta
            ax = int(cx + comp_al * math.cos(a_al))
            ay = int(cy + comp_al * math.sin(a_al))
            pygame.draw.circle(surface, (255,200,0), (ax,ay), 5)

        # ── Ponteiro das horas (smooth) ──────────────────
        a_h = self._ang(hor + mnt/60 + seg/3600, 12)
        self._ponteiro(surface, cx, cy, a_h, raio*0.50, (60,200,60), 8)
        # brilho central
        self._ponteiro(surface, cx, cy, a_h, raio*0.45, (120,255,120), 3)

        # ── Ponteiro dos minutos (smooth) ────────────────
        a_m = self._ang(mnt + seg/60, 60)
        self._ponteiro(surface, cx, cy, a_m, raio*0.75, (60,120,255), 5)
        self._ponteiro(surface, cx, cy, a_m, raio*0.70, (120,180,255), 2)

        # ── Ponteiro dos segundos ────────────────────────
        a_s = self._ang(seg, 60)
        self._ponteiro(surface, cx, cy, a_s,  raio*0.87, (255,60,60), 2)
        # rabinho
        xr = cx - raio*0.14*math.cos(a_s)
        yr = cy - raio*0.14*math.sin(a_s)
        pygame.draw.line(surface, (255,60,60), (cx,cy), (int(xr),int(yr)), 3)

        # ── Centro ───────────────────────────────────────
        pygame.draw.circle(surface, (220,225,235), (cx,cy), 10)
        pygame.draw.circle(surface, (255,60,60),   (cx,cy), 5)
        pygame.draw.circle(surface, (255,255,255), (cx,cy), 2)

        # ── Label hora digital ───────────────────────────
        fn = fonts['sm']
        t_obj = time.localtime()
        hora_str = f"{t_obj.tm_hour:02d}:{mnt:02d}:{seg:02d}"
        lbl = fn.render(hora_str, True, (180, 200, 240))
        surface.blit(lbl, (cx - lbl.get_width()//2, cy + int(raio*0.30)))

        # ── Alarme HUD ───────────────────────────────────
        al_cor = (255, 200, 0) if self._show_alarm else (80, 80, 80)
        al_txt = f"⏰ Alarme: {self._alarm_h:02d}:{self._alarm_m:02d}  {'●' if self._show_alarm else '○'}"
        al_lbl = fn.render(al_txt, True, al_cor)
        surface.blit(al_lbl, (cx - al_lbl.get_width()//2, cy - int(raio*0.22)))
