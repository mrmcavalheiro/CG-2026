"""
============================================================
 main.py  —  PONTO DE ENTRADA DA APLICAÇÃO
 UNIJUI · Computação Gráfica · Versão Alfa

 Como executar:
     python main.py

 Dependências:
     pip install pygame numpy

 Estrutura da janela:
   ┌──────────────────────────────────────────┐
   │  TOP BAR  (título + temas + resolução)   │
   ├──────────┬───────────────────────────────┤
   │          │  [abas do exemplo]            │
   │ SIDEBAR  │                               │
   │ (menu de │   CANVAS  (área de desenho)   │
   │ exemplos)│                               │
   │          │                               │
   ├──────────┴───────────────────────────────┤
   │  FOOTER  (info + FPS)                    │
   └──────────────────────────────────────────┘
============================================================
"""

import sys
import pygame
import config as cfg
from input.handler import InputHandler, KeyMap

# ── Importa todos os exemplos ──────────────────────────────
from exemplos.aula04 import (
    ExTranslacao, ExEscala, ExRotacao, ExCisalhamento,
    ExOpenGL00, ExOpenGL01, ExOpenGL02, ExOpenGL03,
    ExOpenGL04, ExOpenGL05, ExOpenGL06,
)
from exemplos.aula05 import (
    ExWindowViewport, ExProjOrtogonal,
    ExProjPerspectiva, ExClipping,
)
try:
    from exemplos.fundamentos import ExSenoCosseno, ExCirculo
    _HAS_FUND = True
except ImportError:
    _HAS_FUND = False


# ─────────────────────────────────────────────
#  GRUPOS DE EXEMPLOS (aparecem no sidebar)
# ─────────────────────────────────────────────
GROUPS = [
    ("── Fundamentos ──", []),   # preenchido abaixo
    ("── Aula 04 ──", [
        ExTranslacao, ExEscala, ExRotacao, ExCisalhamento,
    ]),
    ("── OpenGL ──", [
        ExOpenGL00, ExOpenGL01, ExOpenGL02, ExOpenGL03,
        ExOpenGL04, ExOpenGL05, ExOpenGL06,
    ]),
    ("── Aula 05 ──", [
        ExWindowViewport, ExProjOrtogonal,
        ExProjPerspectiva, ExClipping,
    ]),
]

if _HAS_FUND:
    GROUPS[0] = ("── Fundamentos ──", [ExSenoCosseno, ExCirculo])
else:
    GROUPS.pop(0)


# ─────────────────────────────────────────────
#  HELPERS DE FONTE
# ─────────────────────────────────────────────
def _build_fonts() -> dict:
    """Cria o dicionário de fontes usado por todos os exemplos."""
    return {
        'sm':  pygame.font.SysFont("monospace", 13),
        'tab': pygame.font.SysFont("segoeui",   14),
        'hd':  pygame.font.SysFont("segoeui",   18, bold=True),
        'lg':  pygame.font.SysFont("segoeui",   22, bold=True),
    }


# ─────────────────────────────────────────────
#  SIDEBAR  (menu lateral de seleção)
# ─────────────────────────────────────────────
class Sidebar:
    """Menu lateral com grupos e botões de exemplos."""

    ITEM_H    = 34
    GROUP_H   = 22
    PAD       = 6

    def __init__(self, groups):
        self._groups  = groups          # [(label, [ExClass, ...])]
        self._items   = []              # [(label, ExClass | None, is_group)]
        self._hover   = -1
        self._active  = 0

        # Flatten para lista de itens
        for glabel, classes in groups:
            self._items.append((glabel, None, True))
            for cls in classes:
                self._items.append((cls.NAME, cls, False))

    def active_class(self):
        """Retorna a classe do exemplo ativo."""
        idx = 0
        for label, cls, is_group in self._items:
            if not is_group:
                if idx == self._active:
                    return cls
                idx += 1
        return None

    def _item_rects(self):
        rects = []
        y = cfg.TOP_BAR_H
        for label, cls, is_group in self._items:
            h = self.GROUP_H if is_group else self.ITEM_H
            rects.append(pygame.Rect(0, y, cfg.SIDE_W, h))
            y += h
        return rects

    def handle_mouse_down(self, pos) -> bool:
        rects = self._item_rects()
        sel_idx = 0
        for i, (r, (label, cls, is_group)) in enumerate(
                zip(rects, self._items)):
            if not is_group:
                if r.collidepoint(pos):
                    self._active = sel_idx
                    return True
                sel_idx += 1
        return False

    def handle_mouse_move(self, pos):
        rects = self._item_rects()
        self._hover = -1
        for i, (r, (label, cls, is_group)) in enumerate(
                zip(rects, self._items)):
            if not is_group and r.collidepoint(pos):
                self._hover = i
                break

    def draw(self, surface, fonts):
        fn_sm  = fonts['sm']
        fn_tab = fonts['tab']

        # Fundo do sidebar
        pygame.draw.rect(surface, cfg.PANEL,
                         (0, cfg.TOP_BAR_H, cfg.SIDE_W,
                          cfg.HEIGHT - cfg.TOP_BAR_H - cfg.FOOTER_H))
        pygame.draw.line(surface, cfg.BORDER,
                         (cfg.SIDE_W, cfg.TOP_BAR_H),
                         (cfg.SIDE_W, cfg.HEIGHT - cfg.FOOTER_H), 1)

        rects   = self._item_rects()
        sel_idx = 0
        for i, (r, (label, cls, is_group)) in enumerate(
                zip(rects, self._items)):
            if is_group:
                # Cabeçalho de grupo
                pygame.draw.rect(surface, cfg.BG3, r)
                s = fn_sm.render(label, True, cfg.GRAY2)
                surface.blit(s, (r.x + self.PAD, r.centery - s.get_height() // 2))
            else:
                is_active = (sel_idx == self._active)
                is_hover  = (i == self._hover and not is_active)

                if is_active:
                    bg = cfg.SIDE_ACTIVE
                elif is_hover:
                    bg = cfg.SIDE_HOVER
                else:
                    bg = cfg.PANEL

                pygame.draw.rect(surface, bg, r)

                # Barra colorida lateral
                bar_color = cls.COLOR if cls else cfg.GRAY2
                pygame.draw.rect(surface, bar_color,
                                 (r.x, r.y + 4, 4, r.h - 8),
                                 border_radius=2)

                tc = cfg.WHITE if (is_active or is_hover) else cfg.GRAY
                s  = fn_tab.render(label, True, tc)
                surface.blit(s, (r.x + self.PAD + 8,
                                 r.centery - s.get_height() // 2))

                sel_idx += 1


# ─────────────────────────────────────────────
#  TOP BAR
# ─────────────────────────────────────────────
def _draw_topbar(surface, fonts, fps: float, current_exemplo):
    """Desenha a barra superior com título, tema e FPS."""
    r = pygame.Rect(0, 0, cfg.WIDTH, cfg.TOP_BAR_H)
    pygame.draw.rect(surface, cfg.BG2, r)
    pygame.draw.line(surface, cfg.BORDER,
                     (0, cfg.TOP_BAR_H - 1),
                     (cfg.WIDTH, cfg.TOP_BAR_H - 1), 1)

    fn_hd = fonts['hd']
    fn_sm = fonts['sm']

    # Título
    title = cfg.APP_TITLE
    s = fn_hd.render(title, True, cfg.WHITE)
    surface.blit(s, (cfg.SIDE_W + 12, cfg.TOP_BAR_H // 2 - s.get_height() // 2))

    # Exemplo ativo
    if current_exemplo:
        ex_lbl = fn_sm.render(f"│  {current_exemplo.NAME}", True, cfg.GRAY)
        surface.blit(ex_lbl, (cfg.SIDE_W + 12 + s.get_width() + 6,
                               cfg.TOP_BAR_H // 2 - ex_lbl.get_height() // 2))

    # FPS (direita)
    fps_s = fn_sm.render(f"FPS {fps:.0f}", True, cfg.GRAY2)
    surface.blit(fps_s, (cfg.WIDTH - fps_s.get_width() - 10,
                          cfg.TOP_BAR_H // 2 - fps_s.get_height() // 2))

    # Tema (ao lado do FPS)
    theme_s = fn_sm.render(f"Tema: {cfg.current_theme()}", True, cfg.GRAY2)
    surface.blit(theme_s, (cfg.WIDTH - fps_s.get_width() - theme_s.get_width() - 30,
                             cfg.TOP_BAR_H // 2 - theme_s.get_height() // 2))


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
def _draw_footer(surface, fonts):
    fy = cfg.HEIGHT - cfg.FOOTER_H
    pygame.draw.rect(surface, cfg.BG2, (0, fy, cfg.WIDTH, cfg.FOOTER_H))
    pygame.draw.line(surface, cfg.BORDER, (0, fy), (cfg.WIDTH, fy), 1)
    s = fonts['sm'].render(cfg.FOOTER_TEXT, True, cfg.GRAY2)
    surface.blit(s, (cfg.SIDE_W + 8, fy + (cfg.FOOTER_H - s.get_height()) // 2))

    # Atalhos
    atalhos = "[ESP] Animar   [R] Reset   [↑↓←→] Ajustar   [T] Tema"
    sa = fonts['sm'].render(atalhos, True, cfg.GRAY2)
    surface.blit(sa, (cfg.WIDTH - sa.get_width() - 8,
                       fy + (cfg.FOOTER_H - sa.get_height()) // 2))


# ─────────────────────────────────────────────
#  APLICAÇÃO PRINCIPAL
# ─────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption(cfg.APP_TITLE)

    flags  = pygame.RESIZABLE
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT), flags)
    clock  = pygame.time.Clock()
    fonts  = _build_fonts()

    sidebar  = Sidebar(GROUPS)
    handler  = InputHandler()
    keymap   = KeyMap.default()

    # Exemplos instanciados sob demanda (lazy)
    _instances: dict[type, object] = {}

    def get_exemplo():
        cls = sidebar.active_class()
        if cls is None:
            return None
        if cls not in _instances:
            _instances[cls] = cls()
        return _instances[cls]

    running = True

    # ── Callbacks de evento ───────────────────────────────
    def on_quit():
        nonlocal running
        running = False

    def on_resize(w, h):
        nonlocal screen
        cfg.WIDTH  = max(800, w)
        cfg.HEIGHT = max(480, h)
        cfg.update_layout()
        screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT), flags)
        # Reseta posição de janelas flutuantes em todos os exemplos
        for ex in _instances.values():
            if hasattr(ex, 'reset_windows'):
                ex.reset_windows()

    def on_key(key, mod):
        ex = get_exemplo()

        # Tecla T → próximo tema
        if key == pygame.K_t:
            themes = list(cfg.THEMES.keys())
            idx = themes.index(cfg.current_theme())
            cfg.apply_theme(themes[(idx + 1) % len(themes)])
            return

        # Tecla D → direção (rotação) — passada diretamente
        if ex and hasattr(ex, 'handle_extra'):
            ex.handle_extra(key)

        # Atalhos do KeyMap
        action = keymap.get(key)
        if action and ex:
            ex.handle_action(action)

    def on_mouse_down(pos, button):
        if button != 1:
            return
        # Sidebar tem prioridade
        if pos[0] < cfg.SIDE_W:
            sidebar.handle_mouse_down(pos)
            return
        ex = get_exemplo()
        if ex and hasattr(ex, 'handle_mouse_down'):
            ex.handle_mouse_down(pos)

    def on_mouse_move(pos, rel):
        sidebar.handle_mouse_move(pos)
        ex = get_exemplo()
        if ex and hasattr(ex, 'handle_mouse_move'):
            ex.handle_mouse_move(pos)

    def on_mouse_up(pos, button):
        ex = get_exemplo()
        if ex and hasattr(ex, 'handle_mouse_up'):
            ex.handle_mouse_up(pos)

    def on_scroll(x, dy):
        ex = get_exemplo()
        if ex and hasattr(ex, 'handle_scroll'):
            ex.handle_scroll(dy)

    handler.on('on_quit',        on_quit)
    handler.on('on_resize',      on_resize)
    handler.on('on_key',         on_key)
    handler.on('on_mouse_down',  on_mouse_down)
    handler.on('on_mouse_move',  on_mouse_move)
    handler.on('on_mouse_up',    on_mouse_up)
    handler.on('on_scroll',      on_scroll)

    # ── Loop principal ────────────────────────────────────
    while running:
        dt = clock.tick(cfg.FPS) / 1000.0

        events = pygame.event.get()
        if not handler.process(events):
            break

        ex = get_exemplo()

        # Update
        if ex:
            ex.update(dt)

        # Draw
        screen.fill(cfg.BG)

        # Canvas (área do exemplo)
        cx, cy, cw, ch = cfg.canvas_rect()
        pygame.draw.rect(screen, cfg.BG, (cx, cy, cw, ch))

        if ex:
            ex.draw(screen, fonts)
        else:
            # Tela de boas-vindas
            msg  = fonts['lg'].render("← Selecione um exemplo no menu", True, cfg.GRAY)
            screen.blit(msg, (cx + cw // 2 - msg.get_width() // 2,
                               cy + ch // 2 - msg.get_height() // 2))

        # UI fixa (desenhada por cima do canvas)
        sidebar.draw(screen, fonts)
        _draw_topbar(screen, fonts, clock.get_fps(), ex)
        _draw_footer(screen, fonts)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
