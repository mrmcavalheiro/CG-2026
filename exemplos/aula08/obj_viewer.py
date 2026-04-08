"""
============================================================
 exemplos/aula08/obj_viewer.py

 Visualizador de Arquivos OBJ com 4 modos de visualização

 Toolbar (topo):
  [Abrir OBJ]  [Pontos]  [Superfícies]  [Cores]

 Modos:
  - Pontos:      apenas vértices como pontos
  - Superfícies: faces preenchidas em cinza + wireframe
  - Cores:       faces preenchidas com cores do MTL ou paleta

 Controles:
  - Setas:  rotacionar objeto
  - ESPAÇO: rotação automática
  - R:      resetar rotação
  - Scroll: rolar código OBJ (painel direito)
============================================================
"""

import os
import math
import pygame
import config as cfg
from exemplos.base import ExemploBase
from exemplos.docs_teoria import DOCS_TEORIA
from interface.tabs import TabBar, TAB_H
from interface.doc_view import DocView
from interface.janela import WindowManager, draw_rows_in_win


# ── Constantes de layout ─────────────────────────────────
TOOLBAR_H = 36
BTN_PAD   = 8

# Modos de visualização
MODE_PONTOS = 0
MODE_WIRE   = 1
MODE_SUPERF = 2
MODE_CORES  = 3

# ── Constantes da cena 3D ────────────────────────────────
AXIS_LEN = 1.8              # comprimento de cada semi-eixo
_AX_R    = (220,  55,  55)  # cor eixo X
_AX_G    = ( 55, 210,  55)  # cor eixo Y
_AX_B    = ( 55, 110, 230)  # cor eixo Z


# ── Paleta de cores para grupos sem MTL ─────────────────
_PALETTE = [
    (88, 166, 255), (63, 185, 80),  (247, 129, 102),
    (188, 140, 255),(57, 213, 213), (227, 179, 65),
    (255, 100, 100),(100, 200, 180),(200, 160, 80),
    (160, 80, 200), (80, 180, 120), (220, 120, 60),
]


# ── OBJ embutidos de exemplo ─────────────────────────────
OBJ_CUBO = """\
# Cubo — exemplo básico de arquivo OBJ
mtllib cubo.mtl
o Cubo
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0  1.0
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
v  1.0  1.0 -1.0
v -1.0  1.0 -1.0
vn  0  0  1
vn  0  0 -1
vn  0  1  0
vn  0 -1  0
vn  1  0  0
vn -1  0  0
g frente
usemtl vermelho
f 1//1 2//1 3//1 4//1
g traseira
usemtl azul
f 5//2 8//2 7//2 6//2
g topo
usemtl verde
f 4//3 3//3 7//3 8//3
g base
usemtl amarelo
f 1//4 5//4 6//4 2//4
g direita
usemtl laranja
f 2//5 6//5 7//5 3//5
g esquerda
usemtl roxo
f 1//6 4//6 8//6 5//6
"""

OBJ_PIRAMIDE = """\
# Pirâmide — 5 vértices, 5 faces
o Piramide
v -1.0  0.0 -1.0
v  1.0  0.0 -1.0
v  1.0  0.0  1.0
v -1.0  0.0  1.0
v  0.0  2.0  0.0
vn  0 -1  0
vn  0  0.447  0.894
vn  0.894  0.447  0
vn  0  0.447 -0.894
vn -0.894  0.447  0
g base
usemtl cinza
f 1//1 4//1 3//1 2//1
g frente
usemtl ciano
f 1//2 2//2 5//2
g direita
usemtl verde
f 2//3 3//3 5//3
g traseira
usemtl laranja
f 3//4 4//4 5//4
g esquerda
usemtl magenta
f 4//5 1//5 5//5
"""

OBJ_CASA = """\
# Casa — corpo (cubo) + telhado (pirâmide)
o Casa
v -1.5  0.0 -1.0
v  1.5  0.0 -1.0
v  1.5  2.0 -1.0
v -1.5  2.0 -1.0
v -1.5  0.0  1.0
v  1.5  0.0  1.0
v  1.5  2.0  1.0
v -1.5  2.0  1.0
v -1.8  2.0 -1.2
v  1.8  2.0 -1.2
v  1.8  2.0  1.2
v -1.8  2.0  1.2
v  0.0  3.5  0.0
g parede
usemtl branco
f 5 6 7 8
f 1 4 3 2
f 2 3 7 6
f 1 5 8 4
g piso
usemtl cinza
f 1 2 6 5
g telhado
usemtl vermelho
f 9 10 13
f 11 12 13
f 10 11 13
f 12 9 13
"""

# MTL embutido com Kd (cores difusas)
MTL_EMBUTIDO = {
    "vermelho": (220,  60,  60),
    "azul":     ( 60, 100, 220),
    "verde":    ( 60, 180,  80),
    "amarelo":  (220, 180,  50),
    "laranja":  (220, 130,  40),
    "roxo":     (160,  60, 200),
    "cinza":    (140, 140, 150),
    "ciano":    ( 50, 200, 200),
    "magenta":  (200,  60, 180),
    "branco":   (220, 220, 230),
    "preto":    ( 40,  40,  45),
}

EXEMPLOS = [
    ("Cubo",     OBJ_CUBO),
    ("Pirâmide", OBJ_PIRAMIDE),
    ("Casa",     OBJ_CASA),
]


# ════════════════════════════════════════════════════════
#  Parser OBJ + MTL
# ════════════════════════════════════════════════════════

def _parse_mtl_text(text):
    """Retorna dict: nome -> (R,G,B) 0-255 a partir de texto MTL."""
    mats = {}
    cur  = None
    for line in text.splitlines():
        p = line.strip().split()
        if not p: continue
        if p[0] == 'newmtl' and len(p) > 1:
            cur = p[1]
            mats[cur] = (180, 180, 180)
        elif p[0] == 'Kd' and cur and len(p) >= 4:
            r = min(255, int(float(p[1]) * 255))
            g = min(255, int(float(p[2]) * 255))
            b = min(255, int(float(p[3]) * 255))
            mats[cur] = (r, g, b)
    return mats


def _parse_obj(text, mtl_dir=""):
    """
    Retorna:
      verts   — list[(x,y,z)]
      groups  — list[(nome, mat_nome, [face_indices])]
      mtl     — dict[mat_nome -> (R,G,B)]  ou {}
      has_mtl — bool
      raw_lines — list[str]  (linhas brutas para exibição)
    """
    verts    = []
    groups   = []
    mtl      = dict(MTL_EMBUTIDO)   # começa com cores embutidas
    has_mtl  = False
    raw_lines = text.splitlines()

    cur_group = "default"
    cur_mat   = None
    cur_faces = []
    mtllib_file = None

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        p = stripped.split()
        cmd = p[0]

        if cmd == 'v' and len(p) >= 4:
            verts.append((float(p[1]), float(p[2]), float(p[3])))

        elif cmd == 'mtllib' and len(p) > 1:
            mtllib_file = p[1]

        elif cmd == 'o' or cmd == 'g':
            name = p[1] if len(p) > 1 else "default"
            if cur_faces:
                groups.append((cur_group, cur_mat, cur_faces))
            cur_group = name
            cur_faces = []

        elif cmd == 'usemtl' and len(p) > 1:
            if cur_faces:
                groups.append((cur_group, cur_mat, cur_faces))
                cur_faces = []
            cur_mat = p[1]

        elif cmd == 'f' and len(p) >= 4:
            face = []
            for token in p[1:]:
                idx = token.split('/')[0]
                vi  = int(idx) - 1
                face.append(vi)
            cur_faces.append(face)

    if cur_faces:
        groups.append((cur_group, cur_mat, cur_faces))

    # Tentar carregar MTL externo
    if mtllib_file and mtl_dir:
        mtl_path = os.path.join(mtl_dir, mtllib_file)
        if os.path.isfile(mtl_path):
            try:
                with open(mtl_path, encoding='utf-8', errors='replace') as f:
                    external = _parse_mtl_text(f.read())
                mtl.update(external)
                has_mtl = True
            except Exception:
                pass

    # Verificar se algum usemtl corresponde a cores não-embutidas
    for _, mat_name, _ in groups:
        if mat_name and mat_name not in MTL_EMBUTIDO:
            has_mtl = bool(mtllib_file and mtl_dir)
            break

    return verts, groups, mtl, has_mtl, raw_lines


def _auto_center_scale(verts):
    """Retorna verts normalizados para caber em cubo unitário [-1,1]."""
    if not verts:
        return verts
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    cx = (max(xs) + min(xs)) / 2
    cy = (max(ys) + min(ys)) / 2
    cz = (max(zs) + min(zs)) / 2
    ext = max(
        max(xs) - min(xs),
        max(ys) - min(ys),
        max(zs) - min(zs),
        1e-6,
    ) / 2
    return [((x - cx) / ext, (y - cy) / ext, (z - cz) / ext)
            for x, y, z in verts]


# ── Transformações 3D ────────────────────────────────────

def _rot_x(pts, a):
    c, s = math.cos(a), math.sin(a)
    return [(x, y*c - z*s, y*s + z*c) for x,y,z in pts]

def _rot_y(pts, a):
    c, s = math.cos(a), math.sin(a)
    return [(x*c + z*s, y, -x*s + z*c) for x,y,z in pts]

def _rot_z(pts, a):
    c, s = math.cos(a), math.sin(a)
    return [(x*c - y*s, x*s + y*c, z) for x,y,z in pts]

def _project(pts, cx, cy, scale, d=4.5):
    result = []
    for x, y, z in pts:
        dz = z + d
        if abs(dz) < 0.01: dz = 0.01
        xp = int(cx + (d * x / dz) * scale)
        yp = int(cy - (d * y / dz) * scale)
        result.append((xp, yp, dz))
    return result


# ── Linha tracejada ─────────────────────────────────────

def _draw_dashed(surface, color, p1, p2, dash=6, gap=4):
    x1, y1 = p1; x2, y2 = p2
    dx = x2 - x1; dy = y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 1: return
    ux, uy = dx / ln, dy / ln
    step = dash + gap
    d = 0.0
    while d < ln:
        ax = x1 + ux * d;        ay = y1 + uy * d
        bx = x1 + ux * min(d + dash, ln)
        by = y1 + uy * min(d + dash, ln)
        pygame.draw.line(surface, color, (int(ax), int(ay)), (int(bx), int(by)), 1)
        d += step


# ── Face depth sort (Painter's Algorithm) ───────────────

def _face_depth(face_indices, proj):
    zs = [proj[i][2] for i in face_indices if i < len(proj)]
    return sum(zs) / len(zs) if zs else 0.0


# ════════════════════════════════════════════════════════
#  Botão da toolbar
# ════════════════════════════════════════════════════════

class _ToolBtn:
    W = 100
    H = 26

    def __init__(self, label, action, color=None):
        self.label   = label
        self.action  = action          # int (modo), None (abrir arquivo), ou callable
        self.color   = color or cfg.BLUE
        self.rect    = pygame.Rect(0, 0, self.W, self.H)
        self.hover   = False
        self.active  = False           # para botões de modo
        self.enabled = True            # False = desabilitado/acinzentado

    def set_pos(self, x, y):
        self.rect.topleft = (x, y)

    def draw(self, surface, font):
        r, g, b = self.color

        if not self.enabled:
            pygame.draw.rect(surface, (22, 24, 28), self.rect, border_radius=5)
            pygame.draw.rect(surface, (48, 50, 55), self.rect, 1, border_radius=5)
            s = font.render(self.label, True, (68, 70, 74))
            surface.blit(s, (self.rect.centerx - s.get_width()//2,
                             self.rect.centery - s.get_height()//2))
            return

        if self.active:
            # Fundo cheio com a cor do botão + texto branco + borda clara
            bg       = self.color
            border_c = (min(255, r + 80), min(255, g + 80), min(255, b + 80))
            fc       = (255, 255, 255)
        elif self.hover:
            # Fundo médio (metade da cor) + texto branco + borda viva
            bg       = (min(255, r // 2 + 12), min(255, g // 2 + 12), min(255, b // 2 + 12))
            border_c = (min(255, r + 70), min(255, g + 70), min(255, b + 70))
            fc       = (255, 255, 255)
        else:
            # Fundo escuro tingido + texto colorido + borda na cor do botão
            bg       = (max(0, r // 6), max(0, g // 6), max(0, b // 6))
            border_c = self.color
            fc       = (min(255, r + 110), min(255, g + 110), min(255, b + 110))

        pygame.draw.rect(surface, bg, self.rect, border_radius=5)
        pygame.draw.rect(surface, border_c, self.rect, 1, border_radius=5)
        s = font.render(self.label, True, fc)
        surface.blit(s, (self.rect.centerx - s.get_width()//2,
                         self.rect.centery - s.get_height()//2))

    def check_hover(self, pos):
        self.hover = self.enabled and self.rect.collidepoint(pos)

    def check_click(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


# ════════════════════════════════════════════════════════
#  Exemplo principal
# ════════════════════════════════════════════════════════

class ExObjViewer(ExemploBase):
    NAME  = "Leitor OBJ"
    COLOR = cfg.GREEN

    def __init__(self):
        super().__init__()
        self.angle_x   = 0.0
        self.angle_y   = 0.5
        self.angle_z   = 0.0
        self.auto_spin = False
        # câmera orbital (modo câmera)
        self._cam_x    = 0.0
        self._cam_y    = 0.5
        self._cam_z    = 0.0
        # controles de rotação / translação
        self._rot_mode   = 'object'  # 'object' ou 'camera'
        self._rot_axis   = 'Y'       # eixo ativo: 'X', 'Y' ou 'Z'
        self._trans_mode = False     # False=rotação  True=translação
        # translação do objeto
        self._trans_x = 0.0
        self._trans_y = 0.0
        self._trans_z = 0.0
        self._rot_mode_rect   = pygame.Rect(0, 0, 0, 0)
        self._rot_axis_rects  = {}
        self._trans_btn_rect  = pygame.Rect(0, 0, 0, 0)
        self._code_scroll = 0
        self._mtl_scroll  = 0
        self._code_view   = 'obj'      # 'obj' ou 'mtl'
        self._mtl_raw_lines = []
        self._code_tab_rects = {}      # preenchido no draw
        self._mode     = MODE_SUPERF   # modo inicial
        self._ex_idx   = 0             # índice do exemplo embutido
        self._file_path = ""           # caminho do OBJ externo carregado
        self._has_ext_mtl = False
        self._mtl_file_path = ""       # caminho do MTL carregado manualmente
        self._has_valid_mtl = False    # controla habilitação do botão Cores
        self._show_axes   = True       # toggle eixos 3D
        self._show_labels = True       # toggle labels P1..Pn (modo Pontos)
        self._axis_len    = AXIS_LEN   # comprimento dinâmico dos eixos
        self._axes_btn_rect   = pygame.Rect(0, 0, 0, 0)
        self._axis_minus_rect = pygame.Rect(0, 0, 0, 0)
        self._axis_plus_rect  = pygame.Rect(0, 0, 0, 0)
        self._labels_btn_rect = pygame.Rect(0, 0, 0, 0)
        self._mgr      = None

        self._teoria = DocView(
            fallback_blocks=DOCS_TEORIA["obj_formato"],
            download_pdf=cfg.root_path("teoria", "Aula_08", "obj_formato.pdf"),
        )
        self._teoria.set_tab_offset(TAB_H)
        self._tabs = TabBar(["Demonstração", "Teoria"])

        # Botões da toolbar
        self._btns = [
            _ToolBtn("Abrir OBJ",    None,         (40, 140,  60)),
            _ToolBtn("Abrir MTL",    "mtl",        (160, 110,  30)),
            _ToolBtn("Pontos",       MODE_PONTOS,  (50,  80, 200)),
            _ToolBtn("WireFrame",    MODE_WIRE,    (30, 160, 160)),
            _ToolBtn("Superfícies",  MODE_SUPERF,  (40, 120, 180)),
            _ToolBtn("Cores",        MODE_CORES,   (160,  40, 200)),
        ]
        self._update_btn_active()
        self._load_example()

    # ── Carregar dados ──────────────────────────────────

    def _load_example(self):
        nome, texto = EXEMPLOS[self._ex_idx]
        self._obj_nome = nome
        self._raw_lines = texto.splitlines()
        v, g, m, hm, _ = _parse_obj(texto)
        self._verts  = _auto_center_scale(v)
        self._groups = g
        self._mtl    = m
        self._has_ext_mtl = hm
        self._file_path = ""
        self._mtl_file_path = ""
        self._has_valid_mtl = hm
        self._mtl_raw_lines = []
        self._code_view = 'obj'
        self._code_scroll = 0
        self._mtl_scroll  = 0
        # Se estava em Cores sem MTL válido, voltar para Superfícies
        if self._mode == MODE_CORES and not self._has_valid_mtl:
            self._mode = MODE_SUPERF
        self._update_btn_active()

    def _load_file(self, path):
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                text = f.read()
            mtl_dir = os.path.dirname(path)
            v, g, m, hm, raw = _parse_obj(text, mtl_dir)
            self._verts  = _auto_center_scale(v)
            self._groups = g
            self._mtl    = m
            self._has_ext_mtl = hm
            self._raw_lines   = raw
            self._obj_nome    = os.path.basename(path)
            self._file_path   = path
            self._mtl_file_path = ""
            self._has_valid_mtl = hm
            self._mtl_raw_lines = []
            self._code_view = 'obj'
            self._code_scroll = 0
            self._mtl_scroll  = 0
            # Tentar carregar linhas brutas do MTL referenciado pelo OBJ
            if hm:
                for line in raw:
                    s = line.strip().split()
                    if s and s[0] == 'mtllib' and len(s) > 1:
                        mtl_p = os.path.join(mtl_dir, s[1])
                        if os.path.isfile(mtl_p):
                            try:
                                with open(mtl_p, encoding='utf-8', errors='replace') as mf:
                                    self._mtl_raw_lines = mf.read().splitlines()
                                self._mtl_file_path = mtl_p
                            except Exception:
                                pass
                        break
            # Ativar Cores automaticamente se tem MTL; caso contrário sair do modo Cores
            if hm:
                self._mode = MODE_CORES
            elif self._mode == MODE_CORES:
                self._mode = MODE_SUPERF
            self._update_btn_active()
        except Exception as e:
            self._obj_nome = f"Erro: {e}"

    def _open_file_dialog(self):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            path = filedialog.askopenfilename(
                title="Abrir arquivo OBJ",
                filetypes=[("Wavefront OBJ", "*.obj"),
                           ("Todos os arquivos", "*.*")],
            )
            root.destroy()
            if path:
                self._load_file(path)
        except Exception:
            pass

    def _open_mtl_dialog(self):
        """Abre diálogo para selecionar arquivo MTL e o carrega."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            initial_dir = (os.path.dirname(self._file_path)
                           if self._file_path else "")
            path = filedialog.askopenfilename(
                title="Abrir arquivo MTL",
                initialdir=initial_dir or None,
                filetypes=[("Material Library", "*.mtl"),
                           ("Todos os arquivos", "*.*")],
            )
            root.destroy()
            if path:
                self._load_mtl_file(path)
        except Exception:
            pass

    def _load_mtl_file(self, path):
        """Carrega um arquivo MTL e aplica ao OBJ atual."""
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                text = f.read()
            external = _parse_mtl_text(text)
            if external:
                self._mtl.update(external)
                self._mtl_file_path = path
                self._mtl_raw_lines = text.splitlines()
                self._has_valid_mtl = True
                # Verificar se algum grupo do OBJ usa esses materiais
                mat_names = set(external.keys())
                obj_mats  = {m for _, m, _ in self._groups if m}
                if not mat_names & obj_mats:
                    # MTL carregado mas sem correspondência com os grupos
                    # ainda habilita Cores, mas sem correspondência exata
                    pass
                self._mode = MODE_CORES
                self._update_btn_active()
        except Exception as e:
            self._mtl_file_path = f"Erro: {e}"

    # ── Toolbar ─────────────────────────────────────────

    def _update_btn_active(self):
        for btn in self._btns:
            if isinstance(btn.action, int):
                btn.active = (btn.action == self._mode)
            else:
                btn.active = False   # "Abrir OBJ" / "Abrir MTL" nunca ficam ativos
            # Botão Cores: desabilitado se não há MTL válido
            if btn.action == MODE_CORES:
                btn.enabled = self._has_valid_mtl

    def _layout_btns(self, drx, dry):
        """Posiciona botões na toolbar."""
        x = drx + BTN_PAD
        y = dry + (TOOLBAR_H - _ToolBtn.H) // 2
        for btn in self._btns:
            btn.set_pos(x, y)
            x += _ToolBtn.W + BTN_PAD

    def _draw_toolbar(self, surface, fonts, drx, dry, drw):
        pygame.draw.rect(surface, cfg.BG2,
                         (drx, dry, drw, TOOLBAR_H))
        pygame.draw.line(surface, cfg.BORDER,
                         (drx, dry + TOOLBAR_H - 1),
                         (drx + drw, dry + TOOLBAR_H - 1))
        self._layout_btns(drx, dry)
        fn = fonts['tab']
        for btn in self._btns:
            btn.draw(surface, fn)

        # Info do arquivo à direita
        fn_sm = fonts['sm']
        info = self._obj_nome
        n_v = len(self._verts)
        n_f = sum(len(fs) for _, _, fs in self._groups)
        n_g = len(self._groups)
        detail = f"  v:{n_v}  f:{n_f}  g:{n_g}"
        has_c = "  [MTL]" if (self._has_ext_mtl or
                              any(m and m in self._mtl
                                  for _, m, _ in self._groups)) else ""
        s = fn_sm.render(info + detail + has_c, True, cfg.GRAY)
        sx = drx + drw - s.get_width() - 8
        sy = dry + (TOOLBAR_H - s.get_height()) // 2
        surface.blit(s, (sx, sy))

    # ── Eventos ─────────────────────────────────────────

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create(
            "Leitor OBJ", cax + 10, cay + TOOLBAR_H + 10, 255, 280,
            color=(20, 120, 50), closable=False)
        self._tabs.bind_mgr(self._mgr)

    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 1:
            return self._teoria.handle_mouse_down(pos)

        # Checar toolbar
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H
        toolbar_rect = pygame.Rect(drx, dry, drw, TOOLBAR_H)
        if toolbar_rect.collidepoint(pos):
            for btn in self._btns:
                if btn.check_click(pos):
                    if btn.action is None:
                        self._open_file_dialog()
                    elif btn.action == "mtl":
                        self._open_mtl_dialog()
                    else:
                        self._mode = btn.action
                        self._update_btn_active()
                    return True

        # Botão Eixos 3D (dentro do viewer)
        if self._axes_btn_rect.collidepoint(pos):
            self._show_axes = not self._show_axes
            return True
        # Botão Rotacionar / Transladar
        if self._trans_btn_rect.collidepoint(pos):
            self._trans_mode = not self._trans_mode
            return True
        # Botão modo rotação (Objeto / Câmera)
        if self._rot_mode_rect.collidepoint(pos):
            self._rot_mode = 'camera' if self._rot_mode == 'object' else 'object'
            return True
        # Botões seleção de eixo
        for axis, r in self._rot_axis_rects.items():
            if r.collidepoint(pos):
                self._rot_axis = axis
                return True
        # Botões + / - do comprimento dos eixos
        if self._axis_minus_rect.collidepoint(pos):
            self._axis_len = max(0.4, round(self._axis_len - 0.2, 1))
            return True
        if self._axis_plus_rect.collidepoint(pos):
            self._axis_len = min(4.0, round(self._axis_len + 0.2, 1))
            return True
        # Botão Labels (canto inferior direito do viewer)
        if self._labels_btn_rect.collidepoint(pos):
            self._show_labels = not self._show_labels
            return True

        # Checar abas do painel de código
        for key, rect in self._code_tab_rects.items():
            if rect.collidepoint(pos):
                if key == 'mtl' and not self._mtl_raw_lines:
                    return True  # desabilitado
                self._code_view = key
                return True

        if self._tabs.active == 0 and self._mgr:
            return self._mgr.handle_mouse_down(pos)
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 1:
            self._teoria.handle_mouse_move(pos)
            return
        for btn in self._btns:
            btn.check_hover(pos)
        if self._mgr:
            self._mgr.handle_mouse_move(pos)

    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        self._teoria.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)

    def handle_scroll(self, dy):
        if self._tabs.active == 1:
            self._teoria.handle_scroll(dy)
            return
        # Scroll no código
        drx, dry, drw, drh = cfg.draw_rect()
        mx, my = pygame.mouse.get_pos()
        code_x = drx + int(drw * 0.50) + 10
        if mx >= code_x:
            if self._code_view == 'mtl':
                self._mtl_scroll = max(0, self._mtl_scroll - dy * 3)
            else:
                self._code_scroll = max(0, self._code_scroll - dy * 3)
        elif self._mgr:
            self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)

    def reset(self):
        self.angle_x   = 0.0
        self.angle_y   = 0.5
        self.angle_z   = 0.0
        self._cam_x    = 0.0
        self._cam_y    = 0.5
        self._cam_z    = 0.0
        self._trans_x  = 0.0
        self._trans_y  = 0.0
        self._trans_z  = 0.0
        self.auto_spin = False
        self._code_scroll = 0

    def toggle_anim(self):
        self.auto_spin = not self.auto_spin

    def _apply_rot(self, delta):
        """Rotaciona no eixo ativo (objeto ou câmera)."""
        if self._rot_mode == 'object':
            if   self._rot_axis == 'X': self.angle_x += delta
            elif self._rot_axis == 'Y': self.angle_y += delta
            elif self._rot_axis == 'Z': self.angle_z += delta
        else:
            if   self._rot_axis == 'X': self._cam_x += delta
            elif self._rot_axis == 'Y': self._cam_y += delta
            elif self._rot_axis == 'Z': self._cam_z += delta

    def _apply_trans(self, delta):
        """Translada o objeto no eixo ativo."""
        step = delta * 0.08
        if   self._rot_axis == 'X': self._trans_x += step
        elif self._rot_axis == 'Y': self._trans_y += step
        elif self._rot_axis == 'Z': self._trans_z += step

    def handle_action(self, action):
        rot_step = math.radians(5)
        mods  = pygame.key.get_mods()
        trans = self._trans_mode or bool(mods & pygame.KMOD_SHIFT)
        if   action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':       self.reset()
        elif action == 'inc':
            if trans: self._apply_trans(-1)
            else:     self._apply_rot(-rot_step)
        elif action == 'dec':
            if trans: self._apply_trans(+1)
            else:     self._apply_rot(+rot_step)
        elif action == 'inc_alt':
            if trans: self._apply_trans(+1)
            else:     self._apply_rot(+rot_step)
        elif action == 'dec_alt':
            if trans: self._apply_trans(-1)
            else:     self._apply_rot(-rot_step)

    def handle_extra(self, key):
        if key == pygame.K_o:
            self._ex_idx = (self._ex_idx + 1) % len(EXEMPLOS)
            self._load_example()
        elif key == pygame.K_HOME:
            self.angle_x = 0.0; self.angle_y = 0.0; self.angle_z = 0.0
            self._cam_x  = 0.0; self._cam_y  = 0.0; self._cam_z  = 0.0
            self._trans_x = 0.0; self._trans_y = 0.0; self._trans_z = 0.0
        elif key == pygame.K_x:
            self._rot_axis = 'X'
        elif key == pygame.K_y:
            self._rot_axis = 'Y'
        elif key == pygame.K_z:
            self._rot_axis = 'Z'

    def update(self, dt):
        if self.auto_spin:
            self._apply_rot(0.7 * dt)

    # ── Renderização ─────────────────────────────────────

    def _draw_scene_extras(self, surface, fn_lbl, cx, cy, scale, viewer_rect):
        """Eixos fixos no mundo (angle=0) + mini-gizmo no canto."""
        d = 4.5
        clip_r = pygame.Rect(*viewer_rect)
        old_clip = surface.get_clip()
        surface.set_clip(clip_r)

        AL = self._axis_len
        ax_world = [
            (0, 0, 0),     # 0 origem
            ( AL, 0, 0),   # 1 +X
            (-AL, 0, 0),   # 2 -X
            (0,  AL, 0),   # 3 +Y
            (0, -AL, 0),   # 4 -Y
            (0, 0,  AL),   # 5 +Z
            (0, 0, -AL),   # 6 -Z
        ]
        # angle_x=0, angle_y=0 → eixos fixos, independentes da rotação do objeto
        ar = _rot_x(ax_world, 0.0)
        ar = _rot_y(ar, 0.0)
        ap = _project(ar, cx, cy, scale, d)
        ori = ap[0]
        ox, oy = int(ori[0]), int(ori[1])

        def _axis3d(pos_p, neg_p, col, lbl):
            dim = (max(0, col[0]//3), max(0, col[1]//3), max(0, col[2]//3))
            _draw_dashed(surface, dim, (ox, oy),
                         (int(neg_p[0]), int(neg_p[1])), 6, 4)
            pygame.draw.line(surface, col, (ox, oy),
                             (int(pos_p[0]), int(pos_p[1])), 2)
            dx = pos_p[0] - ox; dy = pos_p[1] - oy
            ln = max(1, math.hypot(dx, dy))
            ux, uy = dx/ln, dy/ln
            tip = (int(pos_p[0]), int(pos_p[1]))
            a1 = (int(tip[0]-ux*9+(-uy)*4), int(tip[1]-uy*9+ux*4))
            a2 = (int(tip[0]-ux*9-(-uy)*4), int(tip[1]-uy*9-ux*4))
            pygame.draw.polygon(surface, col, [tip, a1, a2])
            s = fn_lbl.render(lbl, True, col)
            surface.blit(s, (int(pos_p[0]+ux*12)-s.get_width()//2,
                             int(pos_p[1]+uy*12)-s.get_height()//2))
            sn = fn_lbl.render(f'-{lbl}', True, dim)
            ndx = ox-neg_p[0]; ndy = oy-neg_p[1]
            nln = max(1, math.hypot(ndx, ndy))
            nux, nuy = ndx/nln, ndy/nln
            surface.blit(sn, (int(neg_p[0]-nux*12)-sn.get_width()//2,
                              int(neg_p[1]-nuy*12)-sn.get_height()//2))

        # Desenha Z primeiro (fica atrás visualmente)
        _axis3d(ap[5], ap[6], _AX_B, 'Z')
        _axis3d(ap[1], ap[2], _AX_R, 'X')
        _axis3d(ap[3], ap[4], _AX_G, 'Y')

        # ── Esfera na origem ──────────────────────────────
        pygame.draw.circle(surface, (20, 25, 40),    (ox, oy), 10)
        pygame.draw.circle(surface, (120, 140, 180), (ox, oy),  7)
        pygame.draw.circle(surface, (200, 215, 255), (ox, oy),  3)
        pygame.draw.circle(surface, (200, 215, 255), (ox, oy),  7, 1)

        # ── Mini-gizmo no canto (referência fixa X=dir, Y=cima, Z=diag) ──
        vx, vy, vw, vh = viewer_rect
        gx = vx + vw - 54
        gy = vy + vh - 54
        GR = 28   # raio do gizmo
        _ZA = math.radians(225)
        gizmo_dirs = {
            'X': ( 1.0,  0.0,      _AX_R),
            'Y': ( 0.0, -1.0,      _AX_G),
            'Z': (math.cos(_ZA), math.sin(_ZA), _AX_B),
        }
        pygame.draw.circle(surface, (18, 22, 32), (gx, gy), GR + 4)
        pygame.draw.circle(surface, (50, 60, 80), (gx, gy), GR + 4, 1)
        fn_g = pygame.font.SysFont("segoeui", 11, bold=True)
        for name, (ux, uy, col) in gizmo_dirs.items():
            ex = int(gx + ux * GR); ey = int(gy + uy * GR)
            pygame.draw.line(surface, col, (gx, gy), (ex, ey), 2)
            pygame.draw.circle(surface, col, (ex, ey), 3)
            sl = fn_g.render(name, True, col)
            surface.blit(sl, (int(ex + ux*7)-sl.get_width()//2,
                              int(ey + uy*7)-sl.get_height()//2))

        surface.set_clip(old_clip)

    def _get_group_color(self, gi, mat_name):
        """Retorna cor do grupo conforme modo."""
        if self._mode == MODE_CORES:
            # MTL tem prioridade; fallback para paleta
            if mat_name and mat_name in self._mtl:
                return self._mtl[mat_name]
            return _PALETTE[gi % len(_PALETTE)]
        if self._mode == MODE_SUPERF:
            # Superfícies: cores da paleta por grupo (igual WireFrame)
            return _PALETTE[gi % len(_PALETTE)]
        return (160, 175, 195)   # cinza para outros modos

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

        # Toolbar
        self._draw_toolbar(surface, fonts, drx, dry, drw)
        content_y  = dry + TOOLBAR_H
        content_h  = drh - TOOLBAR_H

        # ── Layout: esquerda viewer | direita código ──────
        viewer_w = int(drw * 0.52)
        code_x   = drx + viewer_w + 6
        code_w   = drw - viewer_w - 10

        cx = drx + viewer_w // 2
        cy = content_y + content_h // 2
        scale = int(min(viewer_w, content_h) * 0.26)

        # Fundo do viewer
        pygame.draw.rect(surface, (10, 14, 22),
                         (drx, content_y, viewer_w, content_h))
        pygame.draw.rect(surface, cfg.BORDER,
                         (drx, content_y, viewer_w, content_h), 1)

        # Projetar vértices: aplica translação depois da rotação
        tx, ty, tz = self._trans_x, self._trans_y, self._trans_z
        if self._rot_mode == 'object':
            pts = _rot_x(self._verts, self.angle_x)
            pts = _rot_y(pts,         self.angle_y)
            pts = _rot_z(pts,         self.angle_z)
        else:
            pts = _rot_x(self._verts, -self._cam_x)
            pts = _rot_y(pts,         -self._cam_y)
            pts = _rot_z(pts,         -self._cam_z)
        # Translação: desloca o objeto no espaço de visão
        pts = [(x + tx, y + ty, z + tz) for x, y, z in pts]
        proj = _project(pts, cx, cy, scale)

        # ── Modo PONTOS ──────────────────────────────────
        if self._mode == MODE_PONTOS:
            fn_lbl = pygame.font.SysFont("monospace", 13)
            pts_depth = sorted(
                [(proj[i][2], i) for i in range(len(proj))],
                reverse=True
            )
            for depth, i in pts_depth:
                px, py, dz = proj[i]
                sz    = max(2, int(8 - dz * 0.8))
                alpha = max(80, min(255, int(220 - dz * 20)))
                color = (alpha, alpha + 20, min(255, alpha + 60))
                pygame.draw.circle(surface, color, (px, py), sz)
                pygame.draw.circle(surface, cfg.WHITE, (px, py), max(1, sz-1), 1)
                if self._show_labels:
                    lbl = fn_lbl.render(f"P{i+1}", True, (220, 220, 100))
                    surface.blit(lbl, (px + sz + 2, py - lbl.get_height()//2))

            s = fn.render(f"{len(self._verts)} vértices", True, cfg.CYAN)
            surface.blit(s, (drx + 8, content_y + 8))

        # ── Modo WIREFRAME ────────────────────────────────
        elif self._mode == MODE_WIRE:
            all_faces = []
            for gi, (gname, mat_name, faces) in enumerate(self._groups):
                color = _PALETTE[gi % len(_PALETTE)]
                for face in faces:
                    valid = [i for i in face if i < len(proj)]
                    if len(valid) < 2: continue
                    depth = _face_depth(valid, proj)
                    all_faces.append((depth, gi, color, valid))

            all_faces.sort(key=lambda x: x[0], reverse=True)

            for depth, gi, color, valid in all_faces:
                face_pts = [(proj[i][0], proj[i][1]) for i in valid]
                for k in range(len(face_pts)):
                    p1 = face_pts[k]
                    p2 = face_pts[(k + 1) % len(face_pts)]
                    pygame.draw.line(surface, color, p1, p2, 1)

            s = fn.render(f"WireFrame — {len(self._groups)} grupos", True, cfg.CYAN)
            surface.blit(s, (drx + 8, content_y + 8))

        # ── Modo SUPERFÍCIES e CORES ─────────────────────
        else:
            # Luz direcional fixa (cima-esquerda-frente), normalizada
            _lx, _ly, _lz = -0.303, 0.808, -0.505
            AMBIENT = 0.35    # mínimo visível mesmo nas faces traseiras

            all_faces = []
            for gi, (gname, mat_name, faces) in enumerate(self._groups):
                color = self._get_group_color(gi, mat_name)
                for face in faces:
                    valid = [i for i in face if i < len(proj)]
                    if len(valid) < 3:
                        continue

                    # Normal 3D com vértices já rotacionados (antes da projeção)
                    v0, v1, v2 = pts[valid[0]], pts[valid[1]], pts[valid[2]]
                    e1x = v1[0]-v0[0]; e1y = v1[1]-v0[1]; e1z = v1[2]-v0[2]
                    e2x = v2[0]-v0[0]; e2y = v2[1]-v0[1]; e2z = v2[2]-v0[2]
                    nx = e1y*e2z - e1z*e2y
                    ny = e1z*e2x - e1x*e2z
                    nz = e1x*e2y - e1y*e2x
                    nl = math.sqrt(nx*nx + ny*ny + nz*nz)

                    if nl < 1e-8:
                        shade    = AMBIENT
                        is_front = True
                    else:
                        nx /= nl; ny /= nl; nz /= nl
                        # Câmera em z=-d → faces frontais têm nz < 0
                        is_front = nz < 0.0
                        if is_front:
                            dot   = max(0.0, nx*_lx + ny*_ly + nz*_lz)
                            shade = AMBIENT + (1.0 - AMBIENT) * dot
                        else:
                            # Face traseira: ambient apenas — ainda visível
                            shade = AMBIENT

                    depth = _face_depth(valid, proj)
                    all_faces.append((depth, gi, mat_name, color, valid,
                                      shade, is_front))

            # Painter's algorithm: mais distante primeiro
            all_faces.sort(key=lambda x: x[0], reverse=True)

            # Passo 1 — preencher todas as faces
            for depth, gi, mat_name, color, valid, shade, is_front in all_faces:
                face_pts = [(proj[i][0], proj[i][1]) for i in valid]
                shaded = tuple(min(255, int(c * shade)) for c in color)
                pygame.draw.polygon(surface, shaded, face_pts)

            # Passo 2 — wireframe apenas nas faces frontais
            for depth, gi, mat_name, color, valid, shade, is_front in all_faces:
                if not is_front:
                    continue
                face_pts = [(proj[i][0], proj[i][1]) for i in valid]
                pygame.draw.polygon(surface, (50, 55, 70), face_pts, 1)

        # ── Controles dos eixos (canto inferior-esquerdo) ──
        fn_ax  = pygame.font.SysFont("segoeui", 14, bold=True)
        fn_sm2 = pygame.font.SysFont("segoeui", 13, bold=True)
        mx, my = pygame.mouse.get_pos()
        btn_h  = 26
        btn_y  = content_y + content_h - btn_h - 6

        # Botão toggle "Eixos 3D"
        btn_w = 84
        btn_x = drx + 6
        self._axes_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        _hov = self._axes_btn_rect.collidepoint((mx, my))
        if self._show_axes:
            _bg = (30, 90, 160) if not _hov else (50, 120, 200)
            _bc = (80, 160, 255); _fc = (230, 240, 255)
        else:
            _bg = (20, 28, 38)  if not _hov else (30, 44, 58)
            _bc = (60, 80, 110); _fc = (90, 120, 160)
        pygame.draw.rect(surface, _bg, self._axes_btn_rect, border_radius=5)
        pygame.draw.rect(surface, _bc, self._axes_btn_rect, 1, border_radius=5)
        _t = fn_ax.render("Eixos 3D", True, _fc)
        surface.blit(_t, (self._axes_btn_rect.centerx - _t.get_width()//2,
                          self._axes_btn_rect.centery - _t.get_height()//2))

        # Widget  [ - ] [ Eixo 1.8 ] [ + ]
        gap   = 6
        sb_w  = 26   # largura dos botões - e +
        mid_w = 62   # largura do label central
        wx    = btn_x + btn_w + gap
        wy    = btn_y
        wh    = btn_h

        self._axis_minus_rect = pygame.Rect(wx,                  wy, sb_w,  wh)
        mid_rect              = pygame.Rect(wx + sb_w,           wy, mid_w, wh)
        self._axis_plus_rect  = pygame.Rect(wx + sb_w + mid_w,   wy, sb_w,  wh)

        # Botões - e +
        for r, sym in [(self._axis_minus_rect, '−'), (self._axis_plus_rect, '+')]:
            _hov2 = r.collidepoint((mx, my))
            pygame.draw.rect(surface, (50, 55, 70) if _hov2 else (28, 32, 42),
                             r, border_radius=5)
            pygame.draw.rect(surface, (100, 110, 140), r, 1, border_radius=5)
            _s = fn_sm2.render(sym, True, (200, 210, 240))
            surface.blit(_s, (r.centerx - _s.get_width()//2,
                              r.centery - _s.get_height()//2))

        # Label central "Eixo" + valor
        pygame.draw.rect(surface, (18, 22, 32), mid_rect, border_radius=4)
        pygame.draw.rect(surface, (70, 80, 110), mid_rect, 1, border_radius=4)
        _lt = pygame.font.SysFont("segoeui", 11).render("Eixo", True, (140, 155, 190))
        _lv = pygame.font.SysFont("segoeui", 12, bold=True).render(
            f"{self._axis_len:.1f}", True, (210, 220, 255))
        surface.blit(_lt, (mid_rect.centerx - _lt.get_width()//2,
                           mid_rect.top + 3))
        surface.blit(_lv, (mid_rect.centerx - _lv.get_width()//2,
                           mid_rect.bottom - _lv.get_height() - 2))

        # ── Eixos, esfera (condicional) ───────────────────
        if self._show_axes:
            self._draw_scene_extras(
                surface, fn_ax, cx, cy, scale,
                (drx, content_y, viewer_w, content_h)
            )

        # ── Painel de controle (centro inferior do viewer) ────
        fn_rot  = pygame.font.SysFont("segoeui", 12, bold=True)
        fn_hint = pygame.font.SysFont("segoeui", 11)
        PNL_H = 56
        PNL_W = 320
        pnl_x = drx + (viewer_w - PNL_W) // 2
        pnl_y = content_y + content_h - PNL_H - 6

        pygame.draw.rect(surface, (12, 16, 26),
                         (pnl_x, pnl_y, PNL_W, PNL_H), border_radius=7)
        pygame.draw.rect(surface, (45, 55, 85),
                         (pnl_x, pnl_y, PNL_W, PNL_H), 1, border_radius=7)

        axis_colors = {'X': _AX_R, 'Y': _AX_G, 'Z': _AX_B}
        mods   = pygame.key.get_mods()
        _shift = bool(mods & pygame.KMOD_SHIFT)
        bh = 20

        # ── Linha 1: [Rot|Trans]  [Obj|Cam]  [X][Y][Z] ──────
        L1_Y = pnl_y + 4
        bx   = pnl_x + 6

        # Botão Rot / Trans
        rt_w = 62
        self._trans_btn_rect = pygame.Rect(bx, L1_Y, rt_w, bh)
        _ht = self._trans_btn_rect.collidepoint((mx, my))
        if _shift or self._trans_mode:
            _tbg = (120, 70, 20) if not _ht else (160, 100, 30)
            _tbc = (240, 160, 60); _tfc = (255, 220, 150)
            _tlbl = "Transladar"
        else:
            _tbg = (25, 65, 110) if not _ht else (35, 90, 145)
            _tbc = (80, 150, 230); _tfc = (180, 220, 255)
            _tlbl = "Rotacionar"
        pygame.draw.rect(surface, _tbg, self._trans_btn_rect, border_radius=4)
        pygame.draw.rect(surface, _tbc, self._trans_btn_rect, 1, border_radius=4)
        _ts = fn_rot.render(_tlbl, True, _tfc)
        surface.blit(_ts, (self._trans_btn_rect.centerx - _ts.get_width()//2,
                           self._trans_btn_rect.centery - _ts.get_height()//2))
        bx += rt_w + 5

        # Separador
        pygame.draw.line(surface, (45, 55, 85), (bx, L1_Y + 2), (bx, L1_Y + bh - 2))
        bx += 6

        # Botão Objeto / Câmera
        mode_w = 66
        self._rot_mode_rect = pygame.Rect(bx, L1_Y, mode_w, bh)
        _hm = self._rot_mode_rect.collidepoint((mx, my))
        _is_cam = self._rot_mode == 'camera'
        if _is_cam:
            _mbg = (20, 70, 130) if not _hm else (30, 100, 165)
            _mbc = (60, 150, 240); _mfc = (190, 225, 255)
            _mlbl = "Câmera"
        else:
            _mbg = (25, 80, 45) if not _hm else (35, 110, 60)
            _mbc = (55, 190, 95); _mfc = (170, 250, 190)
            _mlbl = "Objeto"
        pygame.draw.rect(surface, _mbg, self._rot_mode_rect, border_radius=4)
        pygame.draw.rect(surface, _mbc, self._rot_mode_rect, 1, border_radius=4)
        _ms = fn_rot.render(_mlbl, True, _mfc)
        surface.blit(_ms, (self._rot_mode_rect.centerx - _ms.get_width()//2,
                           self._rot_mode_rect.centery - _ms.get_height()//2))
        bx += mode_w + 5

        # Separador
        pygame.draw.line(surface, (45, 55, 85), (bx, L1_Y + 2), (bx, L1_Y + bh - 2))
        bx += 8

        # Label "Eixo:"
        _el = fn_rot.render("Eixo:", True, (100, 115, 145))
        surface.blit(_el, (bx, L1_Y + (bh - _el.get_height())//2))
        bx += _el.get_width() + 4

        # Botões X / Y / Z
        axis_w = 28
        self._rot_axis_rects = {}
        for axis in ('X', 'Y', 'Z'):
            r = pygame.Rect(bx, L1_Y, axis_w, bh)
            self._rot_axis_rects[axis] = r
            _active = (self._rot_axis == axis)
            _hov_a  = r.collidepoint((mx, my))
            col = axis_colors[axis]
            if _active:
                _abg = col; _abc = col; _afc = (10, 10, 10)
            elif _hov_a:
                _abg = tuple(c//2 for c in col)
                _abc = col; _afc = (255, 255, 255)
            else:
                _abg = (18, 22, 32); _abc = tuple(c//2 for c in col)
                _afc = col
            pygame.draw.rect(surface, _abg, r, border_radius=4)
            pygame.draw.rect(surface, _abc, r, 1, border_radius=4)
            _as = fn_rot.render(axis, True, _afc)
            surface.blit(_as, (r.centerx - _as.get_width()//2,
                               r.centery - _as.get_height()//2))
            bx += axis_w + 3

        # ── Linha 2: valores atuais + dica ────────────────────
        L2_Y = L1_Y + bh + 4
        bx2  = pnl_x + 6

        # Valores de rotação (objeto ou câmera)
        if self._rot_mode == 'object':
            ax, ay, az = self.angle_x, self.angle_y, self.angle_z
        else:
            ax, ay, az = self._cam_x, self._cam_y, self._cam_z

        for lbl, val, col in [
            ('Rx', math.degrees(ax), _AX_R),
            ('Ry', math.degrees(ay), _AX_G),
            ('Rz', math.degrees(az), _AX_B),
        ]:
            _sv = fn_hint.render(f"{lbl}:{val:+.0f}°", True, col)
            surface.blit(_sv, (bx2, L2_Y))
            bx2 += _sv.get_width() + 8

        # Valores de translação
        pygame.draw.line(surface, (45, 55, 85),
                         (bx2, L2_Y), (bx2, L2_Y + 14))
        bx2 += 6
        for lbl, val, col in [
            ('Tx', self._trans_x, _AX_R),
            ('Ty', self._trans_y, _AX_G),
            ('Tz', self._trans_z, _AX_B),
        ]:
            _sv = fn_hint.render(f"{lbl}:{val:+.2f}", True, col)
            surface.blit(_sv, (bx2, L2_Y))
            bx2 += _sv.get_width() + 8

        # Dica direita
        _dica = fn_hint.render("Setas=Rot  SHIFT+Setas=Trans  X/Y/Z=Eixo  HOME=Reset",
                               True, (55, 65, 88))
        dx = pnl_x + PNL_W - _dica.get_width() - 6
        if dx > bx2 + 4:
            surface.blit(_dica, (dx, L2_Y))

        # ── Botão "Labels" (canto inferior direito do viewer, só no modo Pontos) ──
        if self._mode == MODE_PONTOS:
            lbl_btn_w, lbl_btn_h = 72, 26
            lbl_btn_x = drx + viewer_w - lbl_btn_w - 6
            lbl_btn_y = content_y + content_h - lbl_btn_h - 6
            self._labels_btn_rect = pygame.Rect(lbl_btn_x, lbl_btn_y,
                                                lbl_btn_w, lbl_btn_h)
            _hov_l = self._labels_btn_rect.collidepoint((mx, my))
            if self._show_labels:
                _lbg = (100, 90, 20) if not _hov_l else (140, 130, 30)
                _lbc = (220, 200, 60); _lfc = (255, 245, 150)
            else:
                _lbg = (22, 26, 34)  if not _hov_l else (32, 36, 48)
                _lbc = (80, 85, 100); _lfc = (100, 110, 130)
            pygame.draw.rect(surface, _lbg, self._labels_btn_rect, border_radius=5)
            pygame.draw.rect(surface, _lbc, self._labels_btn_rect, 1, border_radius=5)
            _ls = fn_ax.render("Labels", True, _lfc)
            surface.blit(_ls, (self._labels_btn_rect.centerx - _ls.get_width()//2,
                               self._labels_btn_rect.centery - _ls.get_height()//2))
        else:
            self._labels_btn_rect = pygame.Rect(0, 0, 0, 0)

        # ── Painel de código (direita) ───────────────────
        CODE_HDR_H = 30
        pygame.draw.rect(surface, (10, 16, 10),
                         (code_x, content_y, code_w, content_h))
        pygame.draw.rect(surface, cfg.GREEN,
                         (code_x, content_y, code_w, content_h), 1)

        # Cabeçalho com abas .obj / .mtl
        pygame.draw.rect(surface, (8, 26, 8),
                         (code_x, content_y, code_w, CODE_HDR_H))
        pygame.draw.line(surface, cfg.GREEN,
                         (code_x, content_y + CODE_HDR_H - 1),
                         (code_x + code_w, content_y + CODE_HDR_H - 1))

        fn_code = pygame.font.SysFont("monospace", 13)
        tab_w, tab_h = 52, 22
        tx = code_x + 5
        ty_tab = content_y + (CODE_HDR_H - tab_h) // 2
        self._code_tab_rects = {}
        for key, label in [('obj', '.obj'), ('mtl', '.mtl')]:
            r = pygame.Rect(tx, ty_tab, tab_w, tab_h)
            has_tab = (key == 'obj') or bool(self._mtl_raw_lines)
            active  = (self._code_view == key)
            if not has_tab:
                bg = (20, 30, 20); fc = (55, 70, 55); bc = (40, 55, 40)
            elif active:
                bg = cfg.GREEN; fc = (10, 14, 10); bc = cfg.GREEN
            else:
                bg = (18, 38, 18); fc = cfg.GREEN; bc = cfg.GREEN
            pygame.draw.rect(surface, bg, r, border_radius=4)
            pygame.draw.rect(surface, bc, r, 1, border_radius=4)
            s = fn_code.render(label, True, fc)
            surface.blit(s, (r.centerx - s.get_width()//2,
                             r.centery - s.get_height()//2))
            self._code_tab_rects[key] = r
            tx += tab_w + 4

        # Linhas a exibir e scroll ativo
        if self._code_view == 'mtl' and self._mtl_raw_lines:
            lines      = self._mtl_raw_lines
            cur_scroll = self._mtl_scroll
        else:
            lines      = self._raw_lines
            cur_scroll = self._code_scroll

        lh = fn_code.get_height() + 2
        code_body_y = content_y + CODE_HDR_H
        code_body_h = content_h - CODE_HDR_H
        max_visible = max(1, code_body_h // lh)
        max_scroll  = max(0, len(lines) - max_visible)
        cur_scroll  = min(cur_scroll, max_scroll)

        # Atualizar scroll armazenado
        if self._code_view == 'mtl':
            self._mtl_scroll = cur_scroll
        else:
            self._code_scroll = cur_scroll

        clip_r = pygame.Rect(code_x + 2, code_body_y, code_w - 10, code_body_h)
        old_clip = surface.get_clip()
        surface.set_clip(clip_r)

        for i, line in enumerate(lines):
            if i < cur_scroll: continue
            row = i - cur_scroll
            if row >= max_visible: break
            y = code_body_y + row * lh
            stripped = line.strip()

            if self._code_view == 'mtl':
                # Sintaxe MTL
                if stripped.startswith('#'):             c = (80, 140, 80)
                elif stripped.startswith('newmtl'):      c = cfg.YELLOW
                elif stripped.lower().startswith('kd'):  c = cfg.ORANGE
                elif stripped.lower().startswith('ka'):  c = (180, 220, 100)
                elif stripped.lower().startswith('ks'):  c = (100, 200, 255)
                elif stripped.lower().startswith('ke'):  c = cfg.CYAN
                elif stripped.lower().startswith('ns'):  c = (200, 160, 80)
                elif stripped.lower().startswith('map_'): c = cfg.PURPLE
                elif stripped.lower().startswith('d ') or stripped.lower().startswith('tr '): c = cfg.GRAY
                else:                                    c = cfg.GRAY
            else:
                # Sintaxe OBJ
                if stripped.startswith('#'):             c = (80, 140, 80)
                elif stripped.startswith('v '):          c = cfg.CYAN
                elif stripped.startswith('vn'):          c = (100, 200, 255)
                elif stripped.startswith('vt'):          c = (100, 220, 200)
                elif stripped.startswith('f '):          c = cfg.ORANGE
                elif stripped.startswith('g '):          c = cfg.GREEN
                elif stripped.startswith('usemtl'):      c = cfg.PURPLE
                elif stripped.startswith('mtllib'):      c = cfg.YELLOW
                elif stripped.startswith('o '):          c = cfg.YELLOW
                else:                                    c = cfg.GRAY

            num = fn_code.render(f"{i+1:3d}", True, (60, 80, 60))
            surface.blit(num, (code_x + 3, y))
            txt = fn_code.render(line, True, c)
            surface.blit(txt, (code_x + 28, y))

        surface.set_clip(old_clip)

        # Scrollbar código
        if max_scroll > 0:
            sb_y0 = code_body_y
            sb_h  = code_body_h
            th    = max(20, int(sb_h * max_visible / max(1, len(lines))))
            ty    = sb_y0 + int((sb_h - th) * cur_scroll / max(1, max_scroll))
            pygame.draw.rect(surface, cfg.BG3,
                             (code_x + code_w - 7, sb_y0, 5, sb_h))
            pygame.draw.rect(surface, cfg.GREEN,
                             (code_x + code_w - 7, ty, 5, th), border_radius=3)

        # ── Painel info ───────────────────────────────────
        n_v = len(self._verts)
        n_f = sum(len(fs) for _, _, fs in self._groups)
        n_g = len(self._groups)
        tem_cores = any(m and m in self._mtl for _, m, _ in self._groups)
        _MODO_NOMES = {
            MODE_PONTOS: "Pontos",
            MODE_WIRE:   "WireFrame",
            MODE_SUPERF: "Superfícies",
            MODE_CORES:  "Cores",
        }
        modo_nome = _MODO_NOMES.get(self._mode, "?")
        mtl_info  = (os.path.basename(self._mtl_file_path)[:16]
                     if self._mtl_file_path and not self._mtl_file_path.startswith("Erro")
                     else ("Embutido" if self._has_valid_mtl else "Nenhum"))

        rows = [
            ("Leitor OBJ",              cfg.GREEN),
            ("",                        cfg.WHITE),
            (f"{self._obj_nome[:20]}",  cfg.YELLOW),
            (f"Vertices: {n_v}",        cfg.CYAN),
            (f"Faces:    {n_f}",        cfg.ORANGE),
            (f"Grupos:   {n_g}",        cfg.GREEN),
            (f"MTL: {mtl_info}",        cfg.PURPLE if self._has_valid_mtl else cfg.GRAY),
            (f"Cores MTL: {'Sim' if tem_cores else 'Nao'}", cfg.PURPLE if tem_cores else cfg.GRAY),
            ("",                        cfg.WHITE),
            (f"Modo: {modo_nome}",      cfg.WHITE),
            ("",                        cfg.WHITE),
            ("[Abrir OBJ] toolbar",     cfg.YELLOW),
            ("[Abrir MTL] toolbar",     cfg.YELLOW),
            ("[O] Exemplo seguinte",    cfg.YELLOW),
            ("[Setas] Rotacionar",      cfg.YELLOW),
            ("[HOME] Alinhar eixos",    cfg.CYAN),
            ("[ESP] Auto-rotar",        cfg.YELLOW),
            ("[Scroll] Rolar codigo",   cfg.YELLOW),
        ]
        def _content(win, surf):
            if win is self._win_info:
                draw_rows_in_win(surf, win, rows)
        self._mgr.draw_managed(surface, fonts, _content)
