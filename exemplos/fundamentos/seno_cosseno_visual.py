"""
============================================================
 exemplos/fundamentos/seno_cosseno_visual.py

 Apresentação interativa e visual de Seno e Cosseno:
   Passo 1 — O círculo unitário e o ângulo
   Passo 2 — O que é cos(t) e sen(t)?
   Passo 3 — Projeções nos eixos
   Passo 4 — Ondas senoidais
   Passo 5 — Tabela de valores notáveis
   Passo 6 — Da teoria ao relógio (ponte)
============================================================
"""
import pygame
import math
import config as cfg
from exemplos.base    import ExemploBase
from interface.tabs   import TabBar, TAB_H
from interface.janela import WindowManager, draw_rows_in_win
from interface.ui     import draw_axes

# ── Paleta local ─────────────────────────────────────────
_C_COS   = (80,  180, 255)   # azul  = cosseno / eixo X
_C_SEN   = (80,  220, 130)   # verde = seno    / eixo Y
_C_ANG   = (255, 200,  50)   # amarelo = ângulo
_C_RAIO  = (200, 200, 220)   # branco suave = raio
_C_PONTO = (255, 100,  60)   # laranja = ponto P
_C_PROJ  = (180, 100, 255)   # roxo = linhas de projeção
_C_ONDA  = (255, 140,  30)   # onda senoidal


# ═══════════════════════════════════════════════════════════
class ExSenoCosseno2(ExemploBase):
    """Apresentação visual passo-a-passo de seno e cosseno."""

    NAME  = "Sen/Cos — Visual"
    COLOR = _C_COS

    PASSOS = [
        "1 — Ângulo",
        "2 — Ponto P",
        "3 — Projeções",
        "4 — Ondas",
        "5 — Tabela",
        "6 — → Relógio",
    ]

    def __init__(self):
        super().__init__()
        self._tabs  = TabBar(["Demonstração", "Teoria"])
        self._mgr   = None
        self._passo = 0          # slide atual (0–5)
        self._angle = 0.0        # ângulo animado (graus)
        self._anim  = True
        self._speed = 30.0       # graus/segundo
        self._teoria = self._make_teoria()
        self._teoria.set_tab_offset(TAB_H)

    # ── Teoria embutida ───────────────────────────────────
    def _make_teoria(self):
        from interface.doc_view import DocView, DOCS, _b,_h,_s,_t,_c,_li,_th,_tr,_eq,_sep,_bl
        key = "_sencoss_visual"
        DOCS[key] = [
            _t("Seno e Cosseno — Do Zero ao Relógio"),
            _s("Fundamentos de Computacao Grafica | UNIJUI 2026"),
            _sep(),
            _h("Passo 1 — O Ângulo"),
            _b("Um angulo mede a abertura entre dois raios com origem comum."
               " O raio inicial aponta para a direita (eixo X positivo)."
               " O angulo cresce no sentido anti-horario (CCW)."),
            _c("0°  → raio aponta para a DIREITA   (leste)"),
            _c("90° → raio aponta para CIMA        (norte)"),
            _c("180°→ raio aponta para a ESQUERDA  (oeste)"),
            _c("270°→ raio aponta para BAIXO       (sul)"),
            _bl(),
            _h("Radianos vs Graus"),
            _b("Python usa RADIANOS internamente. Conversao:"),
            _c("rad = graus * math.pi / 180"),
            _c("t   = math.radians(45)  # jeito pythonic"),
            _bl(),
            _h("Passo 2 — O Círculo Unitário"),
            _b("Pegue um circulo de raio = 1 centrado na origem."
               " Para qualquer angulo t, o ponto P sobre o circulo tem:"),
            _c("P = ( cos(t),  sen(t) )"),
            _c(""),
            _c("Ou com raio R qualquer:"),
            _c("P = ( cx + R * cos(t),  cy + R * sen(t) )"),
            _bl(),
            _h("Passo 3 — As Projeções"),
            _b("cos(t) e a PROJECAO do ponto P sobre o eixo X."
               " sen(t) e a PROJECAO do ponto P sobre o eixo Y."),
            _th("Funcao  |  Eixo  |  Maximos  |  Zeros"),
            _tr("cos(t)  |  X     |  0° e 180°|  90° e 270°"),
            _tr("sen(t)  |  Y     |  90°       |  0° e 180°"),
            _eq("sen²(t) + cos²(t) = 1"),
            _bl(),
            _h("Passo 4 — Ondas"),
            _b("Quando o angulo cresce continuamente, cos e sen traçam ONDAS."
               " A onda completa um ciclo a cada 360 graus (2π rad)."),
            _c("# Gerar uma onda senoidal:"),
            _c("for t in range(0, 360, 5):"),
            _c("    x = t                 # tempo"),
            _c("    y = math.sin(math.radians(t))  # amplitude"),
            _bl(),
            _h("Passo 5 — Tabela de Valores Notáveis"),
            _th("Angulo  |  cos(t)  |  sen(t)"),
            _tr("0°      |  1.000   |  0.000"),
            _tr("30°     |  0.866   |  0.500"),
            _tr("45°     |  0.707   |  0.707"),
            _tr("60°     |  0.500   |  0.866"),
            _tr("90°     |  0.000   |  1.000"),
            _tr("180°    | -1.000   |  0.000"),
            _tr("270°    |  0.000   | -1.000"),
            _tr("360°    |  1.000   |  0.000"),
            _eq("sen²(t) + cos²(t) = 1"),
            _bl(),
            _h("Passo 6 — Do Círculo ao Relógio"),
            _b("O relogio e um circulo unitario APLICADO. Cada ponteiro"
               " e um ponto P que vai de 0° a 360° ao longo do tempo."),
            _c("# Angulo do ponteiro dos segundos:"),
            _c("# 60 segundos = 360° → 1 seg = 6°"),
            _c("ang = seg * 6  →  ang = 2π * seg / 60"),
            _c(""),
            _c("# Mas o relogio começa no TOPO (12h = cima)"),
            _c("# e gira no sentido HORARIO:"),
            _c("ang = 2π * seg / 60  -  π/2"),
            _c(""),
            _c("# Posição da ponta do ponteiro:"),
            _c("px = cx + R * cos(ang)"),
            _c("py = cy + R * sin(ang)   # Y invertido na tela!"),
            _bl(),
            _h("Por que subtrair π/2?"),
            _b("cos(0) aponta para a DIREITA (3h no relogio)."
               " Queremos que ang=0 aponte para CIMA (12h)."
               " Subtrair π/2 (90°) gira o raio inicial para cima."),
            _c("cos(0 - π/2) = cos(-π/2) = 0  → ponta em X=0 (vertical)"),
            _c("sin(0 - π/2) = -1            → ponta em Y=-R (cima, tela inv)"),
        ]
        dv = DocView()
        dv._key    = key
        dv._blocks = DOCS[key]
        dv._loaded = True
        return dv

    # ── Janelas flutuantes ────────────────────────────────
    def _init_windows(self):
        from interface.doc_view import DocView
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info  = self._mgr.create("Passo atual",
            cax+10, cay+10, 270, 290, color=(20,70,140), closable=False)
        self._win_val   = self._mgr.create("Valores",
            cax+10, cay+315, 270, 200, color=(20,100,60), closable=False)
        self._tabs.bind_mgr(self._mgr)

    # ── Lifecycle ─────────────────────────────────────────
    def reset(self):
        self._angle = 0.0
        self._anim  = True
        self._passo = 0

    def toggle_anim(self): self._anim = not self._anim

    def handle_extra(self, key):
        if key == pygame.K_RIGHT or key == pygame.K_e:
            self._passo = (self._passo + 1) % len(self.PASSOS)
        elif key == pygame.K_LEFT or key == pygame.K_q:
            self._passo = (self._passo - 1) % len(self.PASSOS)

    def handle_action(self, action):
        if action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':     self.reset()
        elif action == 'inc_alt':
            self._passo = (self._passo + 1) % len(self.PASSOS)
        elif action == 'dec_alt':
            self._passo = (self._passo - 1) % len(self.PASSOS)

    def update(self, dt):
        if self._anim:
            self._angle = (self._angle + self._speed * dt) % 360

    # ── Eventos ───────────────────────────────────────────
    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 1:
            return self._teoria.handle_mouse_down(pos, cfg.canvas_rect())
        if self._tabs.active == 0 and self._mgr:
            return self._mgr.handle_mouse_down(pos)
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 1: self._teoria.handle_mouse_move(pos)
        elif self._mgr: self._mgr.handle_mouse_move(pos)

    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        self._teoria.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)

    def handle_scroll(self, dy):
        if self._tabs.active == 1: self._teoria.handle_scroll(dy)
        elif self._mgr: self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)

    # ── Draw principal ────────────────────────────────────
    def draw(self, surface, fonts):
        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        if self._tabs.active == 1:
            self._teoria.render(surface)
            return

        # Área de desenho
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cr = (drx, dry, drw, drh)

        # Barra de passos no topo
        self._draw_passo_bar(surface, fonts, drx, dry, drw)

        # Delega para o passo correto
        passo_fn = [
            self._draw_p1_angulo,
            self._draw_p2_ponto,
            self._draw_p3_projecoes,
            self._draw_p4_ondas,
            self._draw_p5_tabela,
            self._draw_p6_relogio,
        ]
        passo_fn[self._passo](surface, fonts, drx, dry, drw, drh)

        # Janelas flutuantes
        t   = math.radians(self._angle)
        cos_t = math.cos(t)
        sen_t = math.sin(t)

        rows_info = self._info_rows(cos_t, sen_t)
        rows_val  = self._val_rows(cos_t, sen_t)

        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            if win is self._win_val:  draw_rows_in_win(surf, win, rows_val)
        self._mgr.draw_managed(surface, fonts, _content)

    # ── Barra de navegação de passos ──────────────────────
    def _draw_passo_bar(self, surface, fonts, drx, dry, drw):
        fn  = fonts['sm']
        n   = len(self.PASSOS)
        bw  = min(160, (drw - 20) // n)
        bh  = 26
        x0  = drx + (drw - bw*n) // 2
        y0  = dry + 4
        for i, nome in enumerate(self.PASSOS):
            rx = x0 + i*bw
            active = (i == self._passo)
            bg  = cfg.TAB_ACTIVE if active else cfg.BG2
            brd = _C_ANG         if active else cfg.BORDER
            pygame.draw.rect(surface, bg,  (rx, y0, bw, bh), border_radius=3)
            pygame.draw.rect(surface, brd, (rx, y0, bw, bh), 2 if active else 1, border_radius=3)
            cor = cfg.WHITE if active else cfg.GRAY
            t   = fn.render(nome, True, cor)
            surface.blit(t, (rx + bw//2 - t.get_width()//2, y0 + bh//2 - t.get_height()//2))

    # ── Helpers geométricos ───────────────────────────────
    def _circle_center(self, drx, dry, drw, drh):
        """Centro do círculo unitário na área de desenho."""
        return drx + drw//2, dry + 60 + (drh - 60)//2

    def _raio(self, drw, drh):
        return int(min(drw, drh - 60) * 0.34)

    def _ponto_p(self, cx, cy, R):
        t = math.radians(self._angle)
        return (cx + R*math.cos(t), cy - R*math.sin(t))

    # ── PASSO 1 — Ângulo ──────────────────────────────────
    def _draw_p1_angulo(self, surface, fonts, drx, dry, drw, drh):
        cx, cy = self._circle_center(drx, dry, drw, drh)
        R = self._raio(drw, drh)
        t = math.radians(self._angle)
        fn = fonts['sm']

        # Círculo
        pygame.draw.circle(surface, cfg.BORDER, (cx,cy), R, 1)
        # Eixos
        pygame.draw.line(surface, (*_C_COS, 180), (cx-R-20,cy), (cx+R+20,cy), 1)
        pygame.draw.line(surface, (*_C_SEN, 180), (cx,cy+R+20), (cx,cy-R-20), 1)

        # Arco do ângulo
        if self._angle > 1:
            try:
                pygame.draw.arc(surface, _C_ANG,
                    (cx-R//3, cy-R//3, 2*R//3, 2*R//3),
                    0, t + 0.001, 3)
            except (ValueError, TypeError): pass  # valores extremos de seno/cosseno

        # Raio
        px = cx + R*math.cos(t)
        py = cy - R*math.sin(t)
        pygame.draw.line(surface, _C_RAIO, (cx,cy), (int(px),int(py)), 2)

        # Ponto P
        pygame.draw.circle(surface, _C_PONTO, (int(px),int(py)), 8)

        # Label ângulo
        lx = cx + R//2 * math.cos(t/2)
        ly = cy - R//2 * math.sin(t/2) - 14
        lbl = fn.render(f"t = {self._angle:.0f}°", True, _C_ANG)
        surface.blit(lbl, (int(lx)-lbl.get_width()//2, int(ly)))

        # Label ponto
        lbl2 = fn.render(f"P = (cos t,  sen t)", True, _C_PONTO)
        surface.blit(lbl2, (int(px)+12, int(py)-8))

        # Marcações dos 4 quadrantes
        for ang_deg, label, off in [(0,"0°",(10,-8)),(90,"90°",(-18,-22)),
                                    (180,"180°",(-38,-8)),(270,"270°",(-18,12))]:
            ax = cx + (R+14)*math.cos(math.radians(ang_deg))
            ay = cy - (R+14)*math.sin(math.radians(ang_deg))
            lx = fn.render(label, True, cfg.GRAY)
            surface.blit(lx, (int(ax)+off[0], int(ay)+off[1]))

        # Instrução
        inst = fn.render("  [ESP] animar   [←/→]  navegar passos   [R] reset", True, cfg.GRAY2)
        surface.blit(inst, (drx + drw//2 - inst.get_width()//2, dry + drh - 24))

    # ── PASSO 2 — Ponto P ─────────────────────────────────
    def _draw_p2_ponto(self, surface, fonts, drx, dry, drw, drh):
        cx, cy = self._circle_center(drx, dry, drw, drh)
        R  = self._raio(drw, drh)
        t  = math.radians(self._angle)
        fn = fonts['sm']

        # Círculo
        pygame.draw.circle(surface, cfg.BORDER, (cx,cy), R, 2)

        # Raio
        px = cx + R*math.cos(t)
        py = cy - R*math.sin(t)
        pygame.draw.line(surface, _C_RAIO, (cx,cy), (int(px),int(py)), 3)

        # Destaque cos e sen
        # Linha cos (horizontal até p)
        pygame.draw.line(surface, _C_COS, (cx,cy), (int(px),cy), 4)
        # Linha sen (vertical de cx até p)
        pygame.draw.line(surface, _C_SEN, (int(px),cy), (int(px),int(py)), 4)

        # Ponto P
        pygame.draw.circle(surface, _C_PONTO, (int(px),int(py)), 10)
        pygame.draw.circle(surface, cfg.WHITE,  (int(px),int(py)), 4)

        # Labels
        cos_v = math.cos(t)
        sen_v = math.sin(t)
        lb_cos = fn.render(f"cos({self._angle:.0f}°) = {cos_v:.3f}", True, _C_COS)
        lb_sen = fn.render(f"sen({self._angle:.0f}°) = {sen_v:.3f}", True, _C_SEN)
        lb_p   = fn.render(f"P = ({cos_v:.2f}, {sen_v:.2f})", True, _C_PONTO)

        mid_cos_x = cx + (px-cx)//2
        surface.blit(lb_cos, (int(mid_cos_x)-lb_cos.get_width()//2, cy+6))
        surface.blit(lb_sen, (int(px)+10, int(cy + (py-cy)/2)-8))
        surface.blit(lb_p,   (int(px)+12, int(py)-20))

        # Fórmula no centro
        frm = fonts['tab'].render("P = ( R·cos(t) ,  R·sen(t) )", True, cfg.WHITE)
        pygame.draw.rect(surface, cfg.BG2,
            (cx - frm.get_width()//2 - 8, dry+36, frm.get_width()+16, frm.get_height()+6),
            border_radius=4)
        surface.blit(frm, (cx - frm.get_width()//2, dry+39))

    # ── PASSO 3 — Projeções ───────────────────────────────
    def _draw_p3_projecoes(self, surface, fonts, drx, dry, drw, drh):
        cx, cy = self._circle_center(drx, dry, drw, drh)
        R  = self._raio(drw, drh)
        t  = math.radians(self._angle)
        fn = fonts['sm']

        # Círculo + eixos
        pygame.draw.circle(surface, cfg.BORDER, (cx,cy), R, 2)
        pygame.draw.line(surface, (*_C_COS,120), (cx-R-30,cy), (cx+R+30,cy), 1)
        pygame.draw.line(surface, (*_C_SEN,120), (cx,cy+R+30), (cx,cy-R-30), 1)

        px = cx + R*math.cos(t)
        py = cy - R*math.sin(t)

        # Raio (branco)
        pygame.draw.line(surface, _C_RAIO, (cx,cy), (int(px),int(py)), 2)

        # Projeção X (linha pontilhada do ponto até o eixo X)
        for step in range(0, int(abs(py-cy)), 8):
            y_s = cy if py > cy else cy
            frac = step / max(abs(py-cy),1)
            ys = cy + (py-cy)*frac
            pygame.draw.circle(surface, _C_COS, (int(px), int(ys)), 1)
        pygame.draw.line(surface, _C_COS, (int(px),int(py)), (int(px),cy), 1)
        # Seta no eixo X
        pygame.draw.circle(surface, _C_COS, (int(px),cy), 7)
        pygame.draw.circle(surface, cfg.BG,  (int(px),cy), 3)

        # Projeção Y (linha pontilhada do ponto até o eixo Y)
        pygame.draw.line(surface, _C_SEN, (int(px),int(py)), (cx,int(py)), 1)
        pygame.draw.circle(surface, _C_SEN, (cx, int(py)), 7)
        pygame.draw.circle(surface, cfg.BG, (cx, int(py)), 3)

        # Ponto P
        pygame.draw.circle(surface, _C_PONTO, (int(px),int(py)), 8)

        # Labels com setas
        cos_v = math.cos(t)
        sen_v = math.sin(t)

        lx = fn.render(f"cos = {cos_v:.3f}", True, _C_COS)
        ly = fn.render(f"sen = {sen_v:.3f}", True, _C_SEN)
        surface.blit(lx, (int(px) - lx.get_width()//2, cy + 12))
        surface.blit(ly, (cx - ly.get_width() - 8, int(py) - ly.get_height()//2))

        # Identidade
        id_val = math.cos(t)**2 + math.sin(t)**2
        id_str = fn.render(f"sen²+cos² = {id_val:.4f}  ≈ 1  ✓", True, (200,200,100))
        surface.blit(id_str, (cx - id_str.get_width()//2, dry + drh - 32))

    # ── PASSO 4 — Ondas ───────────────────────────────────
    def _draw_p4_ondas(self, surface, fonts, drx, dry, drw, drh):
        cx, cy = self._circle_center(drx, dry, drw, drh)
        R  = self._raio(drw, drh)
        t  = math.radians(self._angle)
        fn = fonts['sm']

        # Círculo unitário (esquerda)
        cx_u = drx + R + 60
        cy_u = cy
        pygame.draw.circle(surface, cfg.BORDER, (cx_u, cy_u), R, 2)
        pygame.draw.line(surface, (*_C_COS,80), (cx_u-R-10,cy_u), (cx_u+R+10,cy_u), 1)
        pygame.draw.line(surface, (*_C_SEN,80), (cx_u,cy_u+R+10), (cx_u,cy_u-R-10), 1)

        px = cx_u + R*math.cos(t)
        py = cy_u - R*math.sin(t)
        pygame.draw.line(surface, _C_RAIO, (cx_u,cy_u), (int(px),int(py)), 2)
        pygame.draw.circle(surface, _C_PONTO, (int(px),int(py)), 8)

        # Área da onda (direita)
        ox = cx_u + R + 30   # início x da onda
        ow = drx + drw - ox - 20  # largura disponível
        oy_cos = cy_u - R//2
        oy_sen = cy_u + R//2
        amp    = R // 2

        # Eixos das ondas
        pygame.draw.line(surface, (*_C_COS,60), (ox, oy_cos), (ox+ow, oy_cos), 1)
        pygame.draw.line(surface, (*_C_SEN,60), (ox, oy_sen), (ox+ow, oy_sen), 1)

        # Labels eixos
        surface.blit(fn.render("cos(t)", True, _C_COS), (ox, oy_cos - 18))
        surface.blit(fn.render("sen(t)", True, _C_SEN), (ox, oy_sen - 18))

        # Ondas
        pts_cos = []
        pts_sen = []
        for i in range(ow):
            angle_i = math.radians(self._angle - 360 * i / ow * 2)
            xp = ox + i
            pts_cos.append((xp, int(oy_cos - amp * math.cos(angle_i))))
            pts_sen.append((xp, int(oy_sen - amp * math.sin(angle_i))))

        if len(pts_cos) > 1:
            pygame.draw.lines(surface, _C_COS, False, pts_cos, 2)
            pygame.draw.lines(surface, _C_SEN, False, pts_sen, 2)

        # Linha vertical marcando o ângulo atual
        pygame.draw.line(surface, (*_C_ANG, 180), (ox, oy_cos-amp-10), (ox, oy_sen+amp+10), 1)

        # Ponto atual nas ondas
        pygame.draw.circle(surface, _C_COS, (ox, int(oy_cos - amp*math.cos(t))), 6)
        pygame.draw.circle(surface, _C_SEN, (ox, int(oy_sen - amp*math.sin(t))), 6)

        # Linha conectando círculo → onda
        pygame.draw.line(surface, (*_C_COS,100), (int(px),int(py)),
                         (ox, int(oy_cos - amp*math.cos(t))), 1)

        # Valor atual
        lbl = fn.render(f"t = {self._angle:.0f}°   cos = {math.cos(t):.3f}   sen = {math.sin(t):.3f}",
                        True, cfg.WHITE)
        surface.blit(lbl, (drx + drw//2 - lbl.get_width()//2, dry + drh - 28))

    # ── PASSO 5 — Tabela ──────────────────────────────────
    def _draw_p5_tabela(self, surface, fonts, drx, dry, drw, drh):
        fn  = fonts['sm']
        fn2 = pygame.font.SysFont("monospace", 13, bold=True)
        fn3 = pygame.font.SysFont("segoeui",   13)

        DADOS = [
            (0,   1.000,  0.000),
            (30,  0.866,  0.500),
            (45,  0.707,  0.707),
            (60,  0.500,  0.866),
            (90,  0.000,  1.000),
            (120,-0.500,  0.866),
            (135,-0.707,  0.707),
            (150,-0.866,  0.500),
            (180,-1.000,  0.000),
            (210,-0.866, -0.500),
            (225,-0.707, -0.707),
            (270, 0.000, -1.000),
            (315, 0.707, -0.707),
            (360, 1.000,  0.000),
        ]

        # Cabeçalho
        col_x   = [drx+50, drx+170, drx+320, drx+460]
        hy      = dry + 50
        headers = ["Ângulo", "Radianos", "cos(t)", "sen(t)"]
        hcols   = [cfg.WHITE, _C_ANG, _C_COS, _C_SEN]
        for i, (hdr, col) in enumerate(zip(headers, hcols)):
            s = fn2.render(hdr, True, col)
            surface.blit(s, (col_x[i], hy))
        pygame.draw.line(surface, cfg.BORDER, (drx+40, hy+20), (drx+560, hy+20), 1)

        # Linhas da tabela
        row_h = 26
        ang_atual = round(self._angle / 15) * 15 % 360

        for ri, (ang, cos_v, sen_v) in enumerate(DADOS):
            ry  = hy + 26 + ri * row_h
            highlight = (ang == ang_atual)
            if highlight:
                pygame.draw.rect(surface, (20,50,90), (drx+40, ry-2, 540, row_h-2), border_radius=3)

            rad_v = ang * math.pi / 180
            vals  = [f"{ang}°", f"{rad_v:.4f}", f"{cos_v:+.3f}", f"{sen_v:+.3f}"]
            vcols = [cfg.WHITE, _C_ANG, _C_COS, _C_SEN]
            for i, (val, col) in enumerate(zip(vals, vcols)):
                s = fn3.render(val, True, col if highlight else tuple(c*3//4 for c in col))
                surface.blit(s, (col_x[i], ry))

        # Miniatura do círculo (direita)
        cx_m = drx + drw - 100
        cy_m = dry + (drh)//2
        R_m  = 70
        t    = math.radians(self._angle)
        pygame.draw.circle(surface, cfg.BORDER, (cx_m,cy_m), R_m, 1)
        px = cx_m + R_m*math.cos(t)
        py = cy_m - R_m*math.sin(t)
        pygame.draw.line(surface, _C_RAIO, (cx_m,cy_m), (int(px),int(py)), 2)
        pygame.draw.line(surface, _C_COS,  (cx_m,cy_m), (int(px),cy_m), 3)
        pygame.draw.line(surface, _C_SEN,  (int(px),cy_m),(int(px),int(py)), 3)
        pygame.draw.circle(surface, _C_PONTO, (int(px),int(py)), 7)

        lbl = fn.render(f"{self._angle:.0f}°", True, _C_ANG)
        surface.blit(lbl, (cx_m - lbl.get_width()//2, cy_m + R_m + 8))

    # ── PASSO 6 — Do círculo ao relógio ──────────────────
    def _draw_p6_relogio(self, surface, fonts, drx, dry, drw, drh):
        fn = fonts['sm']

        # Dois círculos: unitário (esq) e relógio (dir)
        half = drw // 2

        # ── Círculo unitário (esquerda) ───────────────────
        cx_u = drx + half//2
        cy_u = dry + 50 + (drh-50)//2
        R_u  = min(half//2 - 30, (drh-50)//2 - 20)
        t    = math.radians(self._angle)

        pygame.draw.circle(surface, cfg.BORDER, (cx_u, cy_u), R_u, 1)
        pygame.draw.line(surface, (*_C_COS,80), (cx_u-R_u-10,cy_u),(cx_u+R_u+10,cy_u),1)
        pygame.draw.line(surface, (*_C_SEN,80), (cx_u,cy_u+R_u+10),(cx_u,cy_u-R_u-10),1)

        px = cx_u + R_u*math.cos(t)
        py = cy_u - R_u*math.sin(t)
        pygame.draw.line(surface, _C_RAIO, (cx_u,cy_u),(int(px),int(py)),2)
        pygame.draw.circle(surface, _C_PONTO,(int(px),int(py)),8)

        lbl_u = fn.render("Círculo Unitário", True, cfg.GRAY)
        surface.blit(lbl_u, (cx_u - lbl_u.get_width()//2, dry+36))

        # Equação
        eq = fn.render("P = (cos t,  sen t)", True, cfg.WHITE)
        surface.blit(eq, (cx_u - eq.get_width()//2, cy_u + R_u + 8))

        # Divisor
        pygame.draw.line(surface, cfg.BORDER, (drx+half, dry+40),(drx+half, dry+drh-20), 1)

        # ── Relógio (direita) ─────────────────────────────
        import time as _time
        t_sys = _time.localtime()
        seg_s = t_sys.tm_sec
        mnt_s = t_sys.tm_min
        hor_s = t_sys.tm_hour % 12

        cx_r = drx + half + half//2
        cy_r = cy_u
        R_r  = R_u

        # Anel
        for dr2 in range(-2,3):
            pygame.draw.circle(surface, (150+dr2*20,160+dr2*20,180+dr2*20),
                               (cx_r,cy_r), R_r+dr2, 1)
        pygame.draw.circle(surface, (18,26,48), (cx_r,cy_r), R_r-3)

        # Marcações das 12 horas
        for h in range(12):
            a_h = h * (2*math.pi/12) - math.pi/2
            r1  = R_r - 5; r2 = R_r - 16
            x1 = cx_r + r1*math.cos(a_h); y1 = cy_r + r1*math.sin(a_h)
            x2 = cx_r + r2*math.cos(a_h); y2 = cy_r + r2*math.sin(a_h)
            pygame.draw.circle(surface, (200,210,230), (int(x2),int(y2)), 3)

        # Função de ponteiro
        def ponteiro(ang_rad, comp, cor, esp):
            end_x = cx_r + comp*math.cos(ang_rad)
            end_y = cy_r + comp*math.sin(ang_rad)
            pygame.draw.line(surface, cor,(cx_r,cy_r),(int(end_x),int(end_y)),esp)

        # Horas
        a_hora = (hor_s + mnt_s/60)*2*math.pi/12 - math.pi/2
        ponteiro(a_hora, R_r*0.50, (60,200,60), 7)
        # Minutos
        a_min  = (mnt_s + seg_s/60)*2*math.pi/60 - math.pi/2
        ponteiro(a_min,  R_r*0.75, (80,140,255), 4)
        # Segundos
        a_seg  = seg_s * 2*math.pi/60 - math.pi/2
        ponteiro(a_seg,  R_r*0.87, (255,60,60), 2)
        pygame.draw.circle(surface, (255,60,60), (cx_r,cy_r), 5)

        lbl_r = fn.render("Relógio Analógico", True, cfg.GRAY)
        surface.blit(lbl_r, (cx_r - lbl_r.get_width()//2, dry+36))

        # Equações do relógio
        eqs = [
            (f"ang_seg  = 2π × {seg_s}/60 − π/2  = {a_seg:.3f} rad",   (255,100,100)),
            (f"ang_min  = 2π × {mnt_s}/60 − π/2  = {a_min:.3f} rad",   (100,140,255)),
            (f"ang_hora = 2π × {hor_s}/12 − π/2  = {a_hora:.3f} rad",  (100,200,100)),
        ]
        for i,(txt,cor) in enumerate(eqs):
            s = fn.render(txt, True, cor)
            surface.blit(s,(drx + drw//2 - s.get_width()//2, dry+drh-72+i*22))

        # Seta de conexão visual
        arrow = fn.render("O círculo unitário  IS  o relógio  →", True, _C_ANG)
        surface.blit(arrow,(drx + drw//2 - arrow.get_width()//2, dry+drh-90))

    # ── Conteúdo das janelas flutuantes ───────────────────
    def _info_rows(self, cos_t, sen_t):
        p = self._passo
        explicacoes = [
            [("Passo 1 — O Ângulo",         _C_ANG),
             ("",                            cfg.WHITE),
             ("  t = angulo em graus",       cfg.GRAY),
             ("  0° → direita (eixo X+)",    _C_COS),
             ("  90° → cima (eixo Y+)",      _C_SEN),
             ("  180° → esquerda",           cfg.GRAY),
             ("  270° → baixo",              cfg.GRAY),
             ("",                            cfg.WHITE),
             ("  Radianos:",                 cfg.GRAY),
             ("  rad = graus * π/180",       cfg.WHITE),
             (f"  {self._angle:.0f}° = {math.radians(self._angle):.4f} rad", _C_ANG)],
            [("Passo 2 — Ponto P",           _C_PONTO),
             ("",                            cfg.WHITE),
             ("  P = (cos t,  sen t)",       cfg.WHITE),
             ("  Sobre o círculo unitário",  cfg.GRAY),
             ("",                            cfg.WHITE),
             (f"  t = {self._angle:.1f}°",   _C_ANG),
             (f"  cos = {cos_t:.4f}",        _C_COS),
             (f"  sen = {sen_t:.4f}",        _C_SEN),
             (f"  P = ({cos_t:.2f}, {sen_t:.2f})", _C_PONTO)],
            [("Passo 3 — Projeções",         _C_PROJ),
             ("",                            cfg.WHITE),
             ("  cos → proj. no eixo X",     _C_COS),
             ("  sen → proj. no eixo Y",     _C_SEN),
             ("",                            cfg.WHITE),
             (f"  cos({self._angle:.0f}°) = {cos_t:.4f}", _C_COS),
             (f"  sen({self._angle:.0f}°) = {sen_t:.4f}", _C_SEN),
             ("",                            cfg.WHITE),
             ("  Identidade fundamental:",   cfg.GRAY),
             (f"  {cos_t:.3f}²+{sen_t:.3f}²≈1", (200,200,80))],
            [("Passo 4 — Ondas",             _C_ONDA),
             ("",                            cfg.WHITE),
             ("  Ângulo varia 0→360°",       cfg.GRAY),
             ("  cos e sen traçam ondas",    cfg.GRAY),
             ("  Período = 360° = 2π rad",   cfg.GRAY),
             ("",                            cfg.WHITE),
             (f"  t = {self._angle:.1f}°",   _C_ANG),
             (f"  cos = {cos_t:.4f}",        _C_COS),
             (f"  sen = {sen_t:.4f}",        _C_SEN)],
            [("Passo 5 — Tabela",            cfg.WHITE),
             ("",                            cfg.WHITE),
             ("  Ângulos notáveis:",         cfg.GRAY),
             ("  0°  → cos=1,  sen=0",       cfg.GRAY),
             ("  90° → cos=0,  sen=1",       cfg.GRAY),
             ("  180°→ cos=-1, sen=0",       cfg.GRAY),
             ("  270°→ cos=0,  sen=-1",      cfg.GRAY),
             ("",                            cfg.WHITE),
             (f"  Atual: {self._angle:.0f}°",_C_ANG),
             (f"  cos = {cos_t:.4f}",        _C_COS),
             (f"  sen = {sen_t:.4f}",        _C_SEN)],
            [("Passo 6 — Relógio",           (255,200,100)),
             ("",                            cfg.WHITE),
             ("  Círculo = Relógio!",        (255,200,100)),
             ("",                            cfg.WHITE),
             ("  seg:  2π*s/60 − π/2",      (255,100,100)),
             ("  min:  2π*m/60 − π/2",      (100,140,255)),
             ("  hora: 2π*h/12 − π/2",      (100,200,100)),
             ("",                            cfg.WHITE),
             ("  π/2 → começa no TOPO",      cfg.GRAY),
             ("  Sentido horário na tela",   cfg.GRAY)],
        ]
        return explicacoes[p]

    def _val_rows(self, cos_t, sen_t):
        import time as _time
        t2 = _time.localtime()
        return [
            ("Valores em tempo real:",       cfg.BLUE),
            (f"  Angulo:  {self._angle:.1f}°", _C_ANG),
            (f"  Rad:     {math.radians(self._angle):.4f}", cfg.GRAY),
            (f"  cos(t):  {cos_t:.4f}",      _C_COS),
            (f"  sen(t):  {sen_t:.4f}",      _C_SEN),
            (f"  |P|=     {math.sqrt(cos_t**2+sen_t**2):.4f}", cfg.WHITE),
            ("",                             cfg.WHITE),
            ("Hora do sistema:",             cfg.BLUE),
            (f"  {t2.tm_hour:02d}:{t2.tm_min:02d}:{t2.tm_sec:02d}", cfg.WHITE),
            ("",                             cfg.WHITE),
            ("[←/→ ou Q/E] passos",         cfg.YELLOW),
            ("[ESP] animar  [R] reset",      cfg.YELLOW),
        ]
