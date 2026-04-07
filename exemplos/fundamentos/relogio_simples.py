"""
============================================================
 exemplos/fundamentos/relogio_simples.py

 Relógio Analógico Simples — Resolução do Exercício 01:
   - Círculo externo (anel do relógio)
   - 12 marcações de hora (círculos)
   - 3 ponteiros: verde=horas, azul=minutos, vermelho=segundos
   - Sincronizado com time.localtime()

 Aba Demonstração : relógio funcionando em tempo real
 Aba Resolução    : código-fonte comentado passo a passo
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
from interface.doc_view import DocView, DOCS, _b,_h,_s,_t,_c,_li,_th,_tr,_eq,_sep,_bl

# ── Cores dos ponteiros ───────────────────────────────────
C_HORA = (60,  210,  80)    # verde
C_MIN  = (70,  140, 255)    # azul
C_SEG  = (255,  60,  60)    # vermelho
C_ANEL = (200, 215, 235)    # anel externo
C_MARC = ( 60, 100, 180)    # círculos de marcação

# ── Teoria / Resolução explicada ─────────────────────────
DOCS["_relogio_simples"] = [
    _t("Resolução — Relógio Analógico Simples"),
    _s("Exercício 01 | Fundamentos de CG | UNIJUI 2026"),
    _sep(),
    _h("Visão Geral"),
    _b("O relógio e um circulo unitario aplicado. Cada ponteiro e um ponto P"
       " que percorre o circulo de 0 a 360 graus ao longo do tempo real."),
    _bl(),
    _h("Estrutura do Código"),
    _c("import pygame, math, time"),
    _c(""),
    _c("# 1. Obter a hora do sistema"),
    _c("t   = time.localtime()"),
    _c("seg = t.tm_sec         # 0–59"),
    _c("mnt = t.tm_min         # 0–59"),
    _c("hor = t.tm_hour % 12   # 0–11 (formato 12h)"),
    _bl(),
    _h("Calcular o Ângulo de Cada Ponteiro"),
    _b("A formula geral converte o valor do tempo em angulo radiano."
       " Subtraimos π/2 para que angulo 0 aponte para o topo (12h)."),
    _c("# Segundos: 60 seg = uma volta completa (2π)"),
    _c("ang_seg  = 2*π * seg / 60  -  π/2"),
    _c(""),
    _c("# Minutos: 60 min = uma volta  (movimento suave)"),
    _c("ang_min  = 2*π * (mnt + seg/60) / 60  -  π/2"),
    _c(""),
    _c("# Horas: 12h = uma volta  (movimento suave)"),
    _c("ang_hora = 2*π * (hor + mnt/60) / 12  -  π/2"),
    _eq("sen²(t) + cos²(t) = 1"),
    _bl(),
    _h("Posição da Ponta do Ponteiro"),
    _c("# Dado angulo e comprimento do ponteiro:"),
    _c("px = cx + comp * math.cos(ang)"),
    _c("py = cy + comp * math.sin(ang)"),
    _c(""),
    _c("# Desenhar o ponteiro:"),
    _c("pygame.draw.line(surface, cor, (cx,cy), (int(px),int(py)), esp)"),
    _bl(),
    _h("As 12 Marcações de Hora"),
    _c("for h in range(12):"),
    _c("    ang = h * (2*π/12)  -  π/2"),
    _c("    mx  = cx + raio_marc * math.cos(ang)"),
    _c("    my  = cy + raio_marc * math.sin(ang)"),
    _c("    pygame.draw.circle(surface, C_MARC, (mx, my), 5)"),
    _bl(),
    _h("Código Completo"),
    _c("# Ver aba 'Resolução' para o código completo"),
    _c("# com syntax highlight e botão Copiar."),
]

# ── Código-fonte exibido na aba Resolução ─────────────────
_CODIGO = {
    "relogio_simples.py": [
        '"""',
        'Relogio Analogico Simples',
        'Exercicio 01 — Fundamentos de CG | UNIJUI 2026',
        '',
        'Ponteiros:',
        '  Verde   = horas',
        '  Azul    = minutos',
        '  Vermelho = segundos',
        '',
        'Marcacoes: 12 circulos ao redor do anel',
        '"""',
        'import pygame',
        'import math',
        'import time',
        '',
        '# ── Configuracoes ─────────────────────────────',
        'LARGURA  = 600',
        'ALTURA   = 600',
        'CX       = LARGURA // 2    # centro X',
        'CY       = ALTURA  // 2    # centro Y',
        'RAIO     = 220             # raio do relogio',
        'FPS      = 60',
        '',
        '# ── Cores ─────────────────────────────────────',
        'C_FUNDO  = (15,  20,  35)  # fundo escuro',
        'C_ANEL   = (200, 215, 235) # anel externo',
        'C_MARC   = ( 60, 100, 180) # marcacoes de hora',
        'C_HORA   = ( 60, 210,  80) # verde  = horas',
        'C_MIN    = ( 70, 140, 255) # azul   = minutos',
        'C_SEG    = (255,  60,  60) # vermelho = segundos',
        '',
        '# ── Funcao: calcular angulo do ponteiro ────────',
        'def angulo(valor, total):',
        '    """',
        '    Converte tempo em angulo radiano.',
        '    Origem no topo (12h), sentido horario.',
        '    """',
        '    return 2 * math.pi * valor / total  -  math.pi / 2',
        '',
        '# ── Funcao: desenhar ponteiro ──────────────────',
        'def ponteiro(surface, ang, comprimento, cor, espessura):',
        '    """Desenha um ponteiro a partir do centro."""',
        '    px = CX + comprimento * math.cos(ang)',
        '    py = CY + comprimento * math.sin(ang)',
        '    pygame.draw.line(',
        '        surface, cor,',
        '        (CX, CY),          # base (centro)',
        '        (int(px), int(py)), # ponta',
        '        espessura',
        '    )',
        '',
        '# ── Loop principal ─────────────────────────────',
        'def main():',
        '    pygame.init()',
        '    tela  = pygame.display.set_mode((LARGURA, ALTURA))',
        '    pygame.display.set_caption("Relogio Simples")',
        '    clock = pygame.time.Clock()',
        '',
        '    while True:',
        '        # Eventos',
        '        for ev in pygame.event.get():',
        '            if ev.type == pygame.QUIT:',
        '                return',
        '            if ev.type == pygame.KEYDOWN:',
        '                if ev.key == pygame.K_ESCAPE:',
        '                    return',
        '',
        '        # ── Hora do sistema ────────────────────',
        '        t   = time.localtime()',
        '        seg = t.tm_sec',
        '        mnt = t.tm_min',
        '        hor = t.tm_hour % 12   # formato 12h',
        '',
        '        # ── Limpar tela ────────────────────────',
        '        tela.fill(C_FUNDO)',
        '',
        '        # ── 1. Desenhar anel externo ───────────',
        '        # Varios circulos para simular espessura',
        '        for dr in range(-3, 4):',
        '            pygame.draw.circle(',
        '                tela, C_ANEL,',
        '                (CX, CY), RAIO + dr, 1',
        '            )',
        '',
        '        # ── 2. Fundo interno (disco escuro) ────',
        '        pygame.draw.circle(',
        '            tela, (18, 26, 48),',
        '            (CX, CY), RAIO - 4',
        '        )',
        '',
        '        # ── 3. Marcacoes das 12 horas ──────────',
        '        raio_marc = RAIO - 20   # um pouco dentro do anel',
        '        for h in range(12):',
        '            # angulo de cada marcacao',
        '            ang_h = h * (2 * math.pi / 12)  -  math.pi / 2',
        '            # posicao do circulo de marcacao',
        '            mx = int(CX + raio_marc * math.cos(ang_h))',
        '            my = int(CY + raio_marc * math.sin(ang_h))',
        '            # circulo maior nas 12, 3, 6 e 9',
        '            tamanho = 6 if h % 3 == 0 else 4',
        '            pygame.draw.circle(tela, C_MARC, (mx, my), tamanho)',
        '',
        '        # ── 4. Ponteiro das Horas (verde) ──────',
        '        # Movimento suave: inclui fracao dos minutos',
        '        ang_hora = angulo(hor + mnt / 60.0, 12)',
        '        ponteiro(tela, ang_hora,',
        '                 RAIO * 0.50,   # comprimento = 50% do raio',
        '                 C_HORA, 8)     # espessura 8px',
        '',
        '        # ── 5. Ponteiro dos Minutos (azul) ─────',
        '        # Movimento suave: inclui fracao dos segundos',
        '        ang_min = angulo(mnt + seg / 60.0, 60)',
        '        ponteiro(tela, ang_min,',
        '                 RAIO * 0.75,   # comprimento = 75% do raio',
        '                 C_MIN, 5)',
        '',
        '        # ── 6. Ponteiro dos Segundos (vermelho)',
        '        ang_seg = angulo(seg, 60)',
        '        ponteiro(tela, ang_seg,',
        '                 RAIO * 0.87,   # comprimento = 87% do raio',
        '                 C_SEG, 2)',
        '        # Rabinho do ponteiro de segundos',
        '        rb_x = int(CX - RAIO * 0.12 * math.cos(ang_seg))',
        '        rb_y = int(CY - RAIO * 0.12 * math.sin(ang_seg))',
        '        pygame.draw.line(tela, C_SEG, (CX, CY), (rb_x, rb_y), 3)',
        '',
        '        # ── 7. Centro (parafuso central) ───────',
        '        pygame.draw.circle(tela, (220, 225, 235), (CX, CY), 9)',
        '        pygame.draw.circle(tela, C_SEG,           (CX, CY), 5)',
        '        pygame.draw.circle(tela, (255, 255, 255), (CX, CY), 2)',
        '',
        '        # ── Atualizar tela ─────────────────────',
        '        pygame.display.flip()',
        '        clock.tick(FPS)',
        '',
        '',
        'if __name__ == "__main__":',
        '    main()',
    ],
}


# ═══════════════════════════════════════════════════════════
class ExRelogioSimples(ExemploBase):
    """Relógio analógico simples — resolução do exercício."""

    NAME  = "Relógio Simples"
    COLOR = (255, 80, 80)

    def __init__(self):
        super().__init__()
        self._tabs   = TabBar(["Demonstração", "Resolução", "Teoria"])
        self._viewer = CodeViewer(_CODIGO)
        self._mgr    = None
        # teoria
        dv = DocView()
        dv._key    = "_relogio_simples"
        dv._blocks = DOCS["_relogio_simples"]
        dv._loaded = True
        self._teoria = dv
        self._teoria.set_tab_offset(TAB_H)

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Hora do Sistema",
            cax+10, cay+10, 260, 310, color=(30, 60, 120), closable=False)
        self._win_form = self._mgr.create("Fórmulas",
            cax+10, cay+335, 260, 230, color=(20, 80, 50), closable=False)

    def reset(self): pass
    def update(self, dt): pass   # usa hora real

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

    # ── Draw ─────────────────────────────────────────────
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

        # ── Área de desenho ───────────────────────────────
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H

        # Hora real
        t_s  = time.localtime()
        seg  = t_s.tm_sec
        mnt  = t_s.tm_min
        hor  = t_s.tm_hour % 12

        # Centro e raio do relógio
        cx   = drx + drw // 2
        cy   = dry + drh // 2
        raio = int(min(drw, drh) * 0.38)

        # ── Desenhar o relógio ────────────────────────────
        self._draw_relogio(surface, fonts, cx, cy, raio, hor, mnt, seg)

        # ── Janelas flutuantes ────────────────────────────
        ang_seg  = 2*math.pi*seg/60       - math.pi/2
        ang_min  = 2*math.pi*(mnt+seg/60)/60 - math.pi/2
        ang_hora = 2*math.pi*(hor+mnt/60)/12 - math.pi/2

        rows_info = [
            ("Hora do Sistema:",              cfg.BLUE),
            (f"  {t_s.tm_hour:02d}:{mnt:02d}:{seg:02d}", cfg.WHITE),
            ("",                              cfg.WHITE),
            ("Valores dos ponteiros:",        cfg.BLUE),
            (f"  seg = {seg}",               (255,100,100)),
            (f"  mnt = {mnt}  (+{seg}/60)",  (100,150,255)),
            (f"  hor = {hor}  (+{mnt}/60)",  (100,210,100)),
            ("",                              cfg.WHITE),
            ("Ângulos calculados:",           cfg.BLUE),
            (f"  ang_seg  = {math.degrees(ang_seg+math.pi/2):.1f}°", (255,100,100)),
            (f"  ang_min  = {math.degrees(ang_min+math.pi/2):.1f}°", (100,150,255)),
            (f"  ang_hora = {math.degrees(ang_hora+math.pi/2):.1f}°",(100,210,100)),
        ]
        rows_form = [
            ("Fórmulas:",                     cfg.BLUE),
            ("",                              cfg.WHITE),
            ("  ang = 2π×val/total − π/2",   cfg.WHITE),
            ("",                              cfg.WHITE),
            ("  Segundos (total=60):",        (255,100,100)),
            ("  2π × seg / 60 − π/2",        (255,120,120)),
            ("",                              cfg.WHITE),
            ("  Minutos (total=60):",         (100,150,255)),
            ("  2π × (mnt+seg/60)/60 − π/2", (120,170,255)),
            ("",                              cfg.WHITE),
            ("  Horas (total=12):",           (100,210,100)),
            ("  2π × (hor+mnt/60)/12 − π/2", (120,230,120)),
        ]

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_form: draw_rows_in_win(surf, win, rows_form)

        self._mgr.draw_managed(surface, fonts, _content)

    # ── Relógio puro ─────────────────────────────────────
    def _draw_relogio(self, surface, fonts, cx, cy, raio, hor, mnt, seg):

        # ── 1. Anel externo ───────────────────────────────
        for dr in range(-4, 5):
            lum = 200 - abs(dr) * 18
            pygame.draw.circle(surface, (lum, lum+10, lum+20),
                               (cx, cy), raio + dr, 1)

        # ── 2. Fundo interno ─────────────────────────────
        pygame.draw.circle(surface, (18, 26, 48), (cx, cy), raio - 5)

        # ── 3. Marcações das 12 horas (círculos) ─────────
        raio_marc = raio - 20
        for h in range(12):
            ang_h = h * (2*math.pi/12) - math.pi/2
            mx = int(cx + raio_marc * math.cos(ang_h))
            my = int(cy + raio_marc * math.sin(ang_h))
            # Horas principais (12, 3, 6, 9) maiores
            tam = 6 if h % 3 == 0 else 4
            # Cor diferente para as principais
            cor_m = (180, 200, 230) if h % 3 == 0 else C_MARC
            pygame.draw.circle(surface, (0,0,0), (mx+1,my+1), tam)
            pygame.draw.circle(surface, cor_m, (mx, my), tam)

        # ── 4. Ponteiro das horas (verde, grosso) ─────────
        ang_h = 2*math.pi*(hor + mnt/60)/12 - math.pi/2
        comp_h = raio * 0.50
        # Sombra
        pygame.draw.line(surface, (0,0,0),
            (cx+2, cy+2),
            (int(cx + comp_h*math.cos(ang_h))+2,
             int(cy + comp_h*math.sin(ang_h))+2), 10)
        # Corpo
        pygame.draw.line(surface, C_HORA,
            (cx, cy),
            (int(cx + comp_h*math.cos(ang_h)),
             int(cy + comp_h*math.sin(ang_h))), 8)
        # Brilho interno
        pygame.draw.line(surface, tuple(min(255,c+60) for c in C_HORA),
            (cx, cy),
            (int(cx + comp_h*0.4*math.cos(ang_h)),
             int(cy + comp_h*0.4*math.sin(ang_h))), 3)

        # ── 5. Ponteiro dos minutos (azul, médio) ─────────
        ang_m = 2*math.pi*(mnt + seg/60)/60 - math.pi/2
        comp_m = raio * 0.75
        pygame.draw.line(surface, (0,0,0),
            (cx+2, cy+2),
            (int(cx + comp_m*math.cos(ang_m))+2,
             int(cy + comp_m*math.sin(ang_m))+2), 7)
        pygame.draw.line(surface, C_MIN,
            (cx, cy),
            (int(cx + comp_m*math.cos(ang_m)),
             int(cy + comp_m*math.sin(ang_m))), 5)
        pygame.draw.line(surface, tuple(min(255,c+60) for c in C_MIN),
            (cx, cy),
            (int(cx + comp_m*0.4*math.cos(ang_m)),
             int(cy + comp_m*0.4*math.sin(ang_m))), 2)

        # ── 6. Ponteiro dos segundos (vermelho, fino) ─────
        ang_s = 2*math.pi*seg/60 - math.pi/2
        comp_s = raio * 0.87
        pygame.draw.line(surface, C_SEG,
            (cx, cy),
            (int(cx + comp_s*math.cos(ang_s)),
             int(cy + comp_s*math.sin(ang_s))), 2)
        # Rabinho (vai ao lado oposto)
        rb_x = int(cx - raio*0.13*math.cos(ang_s))
        rb_y = int(cy - raio*0.13*math.sin(ang_s))
        pygame.draw.line(surface, C_SEG, (cx,cy), (rb_x, rb_y), 3)

        # ── 7. Centro ────────────────────────────────────
        pygame.draw.circle(surface, (0,0,0),   (cx+1,cy+1), 10)
        pygame.draw.circle(surface, (210,220,235),(cx,cy), 10)
        pygame.draw.circle(surface, C_SEG,      (cx,cy),  6)
        pygame.draw.circle(surface, (255,255,255),(cx,cy), 2)

        # ── 8. Hora digital abaixo do centro ─────────────
        fn = fonts['sm']
        t_obj = time.localtime()
        hora_str = f"{t_obj.tm_hour:02d}:{mnt:02d}:{seg:02d}"
        lbl = fn.render(hora_str, True, (180, 200, 240))
        surface.blit(lbl, (cx - lbl.get_width()//2, cy + int(raio*0.28)))

        # ── 9. Labels dos ponteiros (legend) ──────────────
        fn_leg = fonts['sm']
        for txt, cor, dy2 in [
            ("● horas",   C_HORA,  -20),
            ("● minutos", C_MIN,    0),
            ("● segundos",C_SEG,   20),
        ]:
            lb = fn_leg.render(txt, True, cor)
            surface.blit(lb, (cx - int(raio*0.95), cy + int(raio*0.70) + dy2))
