"""
============================================================
 exemplos/aula08/cores_iluminacao.py

 Exemplo interativo: Cor e Iluminação 3D — Modelo Phong

 Demonstra:
  - Os 3 componentes: Ambiente, Difusa, Especular
  - Efeito de cada componente em tempo real
  - Posição da luz controlável
  - Shading por face (Flat) e interpolado (Gouraud simplificado)
  - Seleção de material: plástico, metal, borracha, espelho

 Controles:
  - Setas: mover fonte de luz
  - Cima/Baixo: ajustar componente ativa
  - 1/2/3: alternar Ambiente / Difusa / Especular
  - M: trocar material
  - ESPAÇO: rotação automática do objeto
  - R: resetar
============================================================
"""

import pygame
import math
import config as cfg
from exemplos.base import ExemploBase
from exemplos.docs_teoria import DOCS_TEORIA
from interface.tabs import TabBar, TAB_H
from interface.doc_view import DocView
from interface.janela import WindowManager, draw_rows_in_win
from interface.ui import draw_label


# ── Materiais pré-definidos ──────────────────────────────
MATERIAIS = {
    "Plástico":  {"Ka": 0.15, "Kd": 0.8,  "Ks": 0.4,  "Ns": 32,   "cor": (100, 160, 255)},
    "Metal":     {"Ka": 0.05, "Kd": 0.4,  "Ks": 0.95, "Ns": 200,  "cor": (200, 200, 220)},
    "Borracha":  {"Ka": 0.2,  "Kd": 0.9,  "Ks": 0.05, "Ns": 4,    "cor": (60,  180,  80)},
    "Espelho":   {"Ka": 0.0,  "Kd": 0.1,  "Ks": 1.0,  "Ns": 512,  "cor": (230, 230, 255)},
    "Cerâmica":  {"Ka": 0.1,  "Kd": 0.7,  "Ks": 0.6,  "Ns": 96,   "cor": (240, 200, 140)},
}
NOMES_MAT = list(MATERIAIS.keys())


def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def _phong_color(base_color, Ka, Kd, Ks, Ns,
                 normal, light_dir, view_dir,
                 light_color=(1.0, 1.0, 1.0),
                 amb_color=(0.3, 0.3, 0.3)):
    """Calcula cor Phong para um fragmento."""
    nx, ny, nz = normal
    lx, ly, lz = light_dir
    vx, vy, vz = view_dir
    br, bg, bb = base_color[0]/255, base_color[1]/255, base_color[2]/255

    # Ambiente
    ar = Ka * amb_color[0] * br
    ag = Ka * amb_color[1] * bg
    ab = Ka * amb_color[2] * bb

    # Difusa — Lei de Lambert: NdotL
    ndotl = max(0.0, nx*lx + ny*ly + nz*lz)
    dr = Kd * ndotl * light_color[0] * br
    dg = Kd * ndotl * light_color[1] * bg
    db = Kd * ndotl * light_color[2] * bb

    # Especular — reflexão R
    rx = 2*ndotl*nx - lx
    ry = 2*ndotl*ny - ly
    rz = 2*ndotl*nz - lz
    rl = math.sqrt(rx*rx + ry*ry + rz*rz)
    if rl > 0: rx, ry, rz = rx/rl, ry/rl, rz/rl

    rdotv = max(0.0, rx*vx + ry*vy + rz*vz)
    spec  = rdotv ** Ns if rdotv > 0 else 0.0
    sr = Ks * spec * light_color[0]
    sg = Ks * spec * light_color[1]
    sb = Ks * spec * light_color[2]

    return (
        _clamp((ar + dr + sr) * 255),
        _clamp((ag + dg + sg) * 255),
        _clamp((ab + db + sb) * 255),
    )


class ExCoresIluminacao(ExemploBase):
    NAME  = "Cor e Iluminação"
    COLOR = cfg.ORANGE

    def __init__(self):
        super().__init__()
        self.mat_idx    = 0
        self.light_ax   = 0.5    # ângulo da luz eixo X
        self.light_ay   = 0.8    # ângulo da luz eixo Y
        self.obj_ay     = 0.0    # rotação do objeto
        self.auto_spin  = False
        self.show_amb   = True
        self.show_dif   = True
        self.show_esp   = True
        self._mgr       = None
        self._teoria    = DocView(
            fallback_blocks=DOCS_TEORIA["cores_iluminacao"],
            download_pdf=cfg.root_path("teoria", "Aula_08", "cores_iluminacao.pdf"),
        )
        self._teoria.set_tab_offset(TAB_H)
        self._tabs = TabBar(["Demonstração", "Teoria"])

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create(
            "Modelo Phong", cax+10, cay+10, 275, 380,
            color=(160, 60, 10), closable=False)
        self._tabs.bind_mgr(self._mgr)

    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 1:
            return self._teoria.handle_mouse_down(pos)
        if self._tabs.active == 0 and self._mgr:
            return self._mgr.handle_mouse_down(pos)
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 1:
            self._teoria.handle_mouse_move(pos)
        elif self._mgr:
            self._mgr.handle_mouse_move(pos)

    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        self._teoria.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)

    def handle_scroll(self, dy):
        if self._tabs.active == 1:
            self._teoria.handle_scroll(dy)
        elif self._mgr:
            self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)

    def reset(self):
        self.light_ax  = 0.5
        self.light_ay  = 0.8
        self.obj_ay    = 0.0
        self.auto_spin = False
        self.show_amb  = self.show_dif = self.show_esp = True

    def toggle_anim(self):
        self.auto_spin = not self.auto_spin

    def handle_action(self, action):
        step = math.radians(8)
        if   action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':       self.reset()
        elif action == 'inc':         self.light_ay += step
        elif action == 'dec':         self.light_ay -= step
        elif action == 'inc_alt':     self.light_ax -= step
        elif action == 'dec_alt':     self.light_ax += step

    def handle_extra(self, key):
        if key == pygame.K_m:
            self.mat_idx = (self.mat_idx + 1) % len(NOMES_MAT)
        elif key == pygame.K_1:
            self.show_amb = not self.show_amb
        elif key == pygame.K_2:
            self.show_dif = not self.show_dif
        elif key == pygame.K_3:
            self.show_esp = not self.show_esp

    def update(self, dt):
        if self.auto_spin:
            self.obj_ay += 0.8 * dt

    def _sphere_points(self, cx, cy, R, segs=24):
        """Gera pontos de uma esfera como fatias para desenhar."""
        slices = []
        for lat in range(segs + 1):
            phi = math.pi * lat / segs - math.pi / 2
            ring = []
            for lon in range(segs + 1):
                theta = 2 * math.pi * lon / segs
                x = math.cos(phi) * math.cos(theta)
                y = math.sin(phi)
                z = math.cos(phi) * math.sin(theta)
                ring.append((x, y, z))
            slices.append(ring)
        return slices

    def draw(self, surface, fonts):
        if self._mgr is None:
            self._init_windows()
        self._tabs.draw(surface, fonts)
        if self._tabs.active == 1:
            self._teoria.render(surface)
            return

        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        fn = fonts['sm']

        mat_nome = NOMES_MAT[self.mat_idx]
        mat = MATERIAIS[mat_nome]
        Ka  = mat["Ka"] if self.show_amb else 0.0
        Kd  = mat["Kd"] if self.show_dif else 0.0
        Ks  = mat["Ks"] if self.show_esp else 0.0
        Ns  = mat["Ns"]
        base_color = mat["cor"]

        # Posição da luz (em espaço de câmera simplificado)
        lx = math.cos(self.light_ax) * math.sin(self.light_ay)
        ly = math.sin(self.light_ax)
        lz = math.cos(self.light_ax) * math.cos(self.light_ay)
        llen = math.sqrt(lx*lx + ly*ly + lz*lz)
        if llen > 0: lx, ly, lz = lx/llen, ly/llen, lz/llen

        vx, vy, vz = 0.0, 0.0, 1.0  # câmera olha para +Z

        # ── Esfera Phong ─────────────────────────────────
        # Renderizar por latitude/longitude como pixel-por-pixel simulado
        # (com círculos por fatia — aproximação eficiente)
        cx_sphere = drx + int(drw * 0.52)
        cy_sphere = dry + drh // 2
        R = int(min(drw, drh) * 0.30)

        # Fundo escuro para a esfera
        pygame.draw.circle(surface, (15, 15, 25), (cx_sphere, cy_sphere), R + 2)

        # Renderizar a esfera linha por linha
        segs = 60
        for row in range(-R, R + 1, 2):
            r2 = R * R - row * row
            if r2 < 0: continue
            half_w = int(math.sqrt(r2))
            for col in range(-half_w, half_w + 1, 2):
                # Normal na superfície da esfera (rotacionada pelo obj_ay)
                nx_raw = col / R
                ny_raw = -row / R
                nz_raw = math.sqrt(max(0, 1 - nx_raw**2 - ny_raw**2))
                # Rotacionar normal pelo ângulo do objeto
                c, s = math.cos(self.obj_ay), math.sin(self.obj_ay)
                nx = nx_raw * c + nz_raw * s
                ny = ny_raw
                nz = -nx_raw * s + nz_raw * c

                color = _phong_color(
                    base_color, Ka, Kd, Ks, Ns,
                    (nx, ny, nz), (lx, ly, lz), (vx, vy, vz)
                )
                px = cx_sphere + col
                py = cy_sphere + row
                surface.set_at((px, py), color)

        # Contorno da esfera
        pygame.draw.circle(surface, cfg.BORDER, (cx_sphere, cy_sphere), R, 1)

        # Posição da fonte de luz (círculo amarelo)
        lx_px = cx_sphere + int(lx * (R + 40))
        ly_px = cy_sphere - int(ly * (R + 40))
        pygame.draw.line(surface, (*cfg.YELLOW, 100),
                         (cx_sphere, cy_sphere), (lx_px, ly_px), 1)
        pygame.draw.circle(surface, cfg.YELLOW, (lx_px, ly_px), 10)
        pygame.draw.circle(surface, cfg.WHITE,  (lx_px, ly_px), 10, 2)
        for a in range(0, 360, 45):
            ax = math.cos(math.radians(a))
            ay = math.sin(math.radians(a))
            pygame.draw.line(surface, cfg.YELLOW,
                             (lx_px + int(ax*12), ly_px + int(ay*12)),
                             (lx_px + int(ax*20), ly_px + int(ay*20)), 2)
        draw_label(surface, "Luz", lx_px + 12, ly_px - 8, fn, cfg.YELLOW, cfg.BG)

        # ── Barras de componentes ────────────────────────
        bx = drx + 10
        by = dry + drh - 90
        bw = int(drw * 0.35)

        componentes = [
            ("Ambiente",  Ka,        cfg.CYAN,   self.show_amb, "[1]"),
            ("Difusa",    Kd,        cfg.BLUE,   self.show_dif, "[2]"),
            ("Especular", Ks,        cfg.WHITE,  self.show_esp, "[3]"),
        ]
        for i, (nome, val, cor, ativo, tecla) in enumerate(componentes):
            y = by + i * 28
            fc = cor if ativo else cfg.GRAY2
            s = fn.render(f"{tecla} {nome}: {val:.2f}", True, fc)
            surface.blit(s, (bx, y))
            # barra
            pygame.draw.rect(surface, cfg.BG3, (bx + 110, y + 2, bw, 12), border_radius=3)
            if ativo:
                fw = int(val * bw)
                pygame.draw.rect(surface, cor, (bx + 110, y + 2, fw, 12), border_radius=3)

        # Brilho (Ns)
        s = fn.render(f"Brilho (Ns): {Ns}", True, cfg.GRAY)
        surface.blit(s, (bx, by + 3 * 28))

        # Painel lateral
        mat_color = base_color
        rows = [
            ("Modelo Phong",             cfg.ORANGE),
            ("",                         cfg.WHITE),
            (f"Material: {mat_nome}",    cfg.YELLOW),
            (f"[M] Trocar material",     cfg.GRAY),
            ("",                         cfg.WHITE),
            ("I = Ka*La",                cfg.CYAN   if self.show_amb else cfg.GRAY2),
            ("  + Kd*Ld*(N.L)",         cfg.BLUE   if self.show_dif else cfg.GRAY2),
            ("  + Ks*Ls*(R.V)^n",       cfg.WHITE  if self.show_esp else cfg.GRAY2),
            ("",                         cfg.WHITE),
            (f"Ka={mat['Ka']:.2f} (amb)",  cfg.CYAN),
            (f"Kd={mat['Kd']:.2f} (dif)",  cfg.BLUE),
            (f"Ks={mat['Ks']:.2f} (esp)",  cfg.WHITE),
            (f"Ns={mat['Ns']}  (brilho)",  cfg.GRAY),
            ("",                         cfg.WHITE),
            ("[Setas] Mover luz",        cfg.YELLOW),
            ("[1/2/3] Toggle componente",cfg.YELLOW),
            ("[ESP] Rotacionar objeto",  cfg.YELLOW),
        ]
        def _content(win, surf):
            if win is self._win_info:
                draw_rows_in_win(surf, win, rows)
        self._mgr.draw_managed(surface, fonts, _content)
