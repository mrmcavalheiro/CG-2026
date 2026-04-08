"""
main.py - Ponto de entrada da aplicacao
UNIJUI - Computacao Grafica - Versao Alfa
"""

import sys
import pygame
import config as cfg
from input.handler import InputHandler, KeyMap

from exemplos.aula04 import (
    ExTranslacao,
    ExEscala,
    ExRotacao,
    ExCisalhamento,
    ExOpenGL00,
    ExOpenGL01,
    ExOpenGL02,
    ExOpenGL03,
    ExOpenGL04,
    ExOpenGL05,
    ExOpenGL06,
)
from exemplos.aula05 import (
    ExWindowViewport,
    ExProjOrtogonal,
    ExProjPerspectiva,
    ExClipping,
)
from exemplos.aula06 import ExBezierSolucao
from exemplos.aula08 import ExVisualizacao3D, ExCoresIluminacao, ExObjViewer

try:
    from exemplos.fundamentos import ExSenoCosseno, ExCirculo
    _HAS_FUND = True
except ImportError:
    _HAS_FUND = False


AULAS = ["Fundamentos", "Aula 04", "Aula 05", "Aula 06", "Aula 08"]

PROGRAMAS_POR_AULA = {
    "Fundamentos": [],
    "Aula 04": [
        ExTranslacao,
        ExEscala,
        ExRotacao,
        ExCisalhamento,
        ExOpenGL00,
        ExOpenGL01,
        ExOpenGL02,
        ExOpenGL03,
        ExOpenGL04,
        ExOpenGL05,
        ExOpenGL06,
    ],
    "Aula 05": [
        ExWindowViewport,
        ExProjOrtogonal,
        ExProjPerspectiva,
        ExClipping,
    ],
    "Aula 06": [ExBezierSolucao],
    "Aula 08": [ExVisualizacao3D, ExCoresIluminacao, ExObjViewer],
}

if _HAS_FUND:
    PROGRAMAS_POR_AULA["Fundamentos"] = [ExSenoCosseno, ExCirculo]


def _split_indices_for_aula(aula_label: str):
    if aula_label != "Aula 04":
        return []

    # Aula 04: separa Transformacoes e OpenGL
    return [4]


def _build_fonts() -> dict:
    return {
        "sm": pygame.font.SysFont("monospace", 15),
        "tab": pygame.font.SysFont("segoeui", 16),
        "hd": pygame.font.SysFont("segoeui", 20, bold=True),
        "lg": pygame.font.SysFont("segoeui", 25, bold=True),
    }


class SidebarProgramas:
    """Menu lateral somente com os programas da aula ativa."""

    ITEM_H = 34
    HEADER_H = 22
    PAD = 6
    GROUP_GAP = 8

    def __init__(self, items=None, split_indices=None):
        self._items = items or []
        self._split_indices = set(split_indices or [])
        self._hover = -1
        self._active = 0

    def set_items(self, items, split_indices=None):
        self._items = items or []
        self._split_indices = set(split_indices or [])
        self._hover = -1
        self._active = 0 if self._items else -1

    def has_items(self) -> bool:
        return bool(self._items)

    def active_class(self):
        if not self._items or self._active < 0:
            return None
        if self._active >= len(self._items):
            self._active = 0
        return self._items[self._active]

    def _item_rects(self):
        rects = []
        y = cfg.TOP_BAR_H + self.HEADER_H
        for i, _ in enumerate(self._items):
            if i in self._split_indices:
                y += self.GROUP_GAP
            rects.append(pygame.Rect(0, y, cfg.SIDE_W, self.ITEM_H))
            y += self.ITEM_H
        return rects

    def handle_mouse_down(self, pos) -> bool:
        if pos[0] >= cfg.SIDE_W:
            return False
        rects = self._item_rects()
        for i, r in enumerate(rects):
            if r.collidepoint(pos):
                self._active = i
                return True
        return False

    def handle_mouse_move(self, pos):
        rects = self._item_rects()
        self._hover = -1
        for i, r in enumerate(rects):
            if r.collidepoint(pos):
                self._hover = i
                break

    def draw(self, surface, fonts, aula_label):
        fn_sm = fonts["sm"]
        fn_tab = fonts["tab"]

        pygame.draw.rect(
            surface,
            cfg.PANEL,
            (0, cfg.TOP_BAR_H, cfg.SIDE_W, cfg.HEIGHT - cfg.TOP_BAR_H - cfg.FOOTER_H),
        )
        pygame.draw.line(
            surface,
            cfg.BORDER,
            (cfg.SIDE_W, cfg.TOP_BAR_H),
            (cfg.SIDE_W, cfg.HEIGHT - cfg.FOOTER_H),
            1,
        )

        header_rect = pygame.Rect(0, cfg.TOP_BAR_H, cfg.SIDE_W, self.HEADER_H)
        pygame.draw.rect(surface, cfg.BG3, header_rect)
        title_sidebar = f"Programas - {aula_label}"
        if aula_label == "Aula 06":
            title_sidebar += " | Soluções"
        s = fn_sm.render(title_sidebar, True, cfg.GRAY2)
        surface.blit(s, (self.PAD, header_rect.centery - s.get_height() // 2))

        for i, (r, cls) in enumerate(zip(self._item_rects(), self._items)):
            is_active = i == self._active
            is_hover = i == self._hover and not is_active

            if is_active:
                bg = cfg.SIDE_ACTIVE
            elif is_hover:
                bg = cfg.SIDE_HOVER
            else:
                bg = cfg.PANEL

            pygame.draw.rect(surface, bg, r)

            pygame.draw.rect(
                surface,
                getattr(cls, "COLOR", cfg.GRAY2),
                (r.x, r.y + 4, 4, r.h - 8),
                border_radius=2,
            )

            tc = cfg.WHITE if (is_active or is_hover) else cfg.GRAY
            label = getattr(cls, "NAME", cls.__name__)
            txt = fn_tab.render(label, True, tc)
            surface.blit(txt, (r.x + self.PAD + 8, r.centery - txt.get_height() // 2))


class MenuAulasTopbar:
    """Abas de aulas na area superior."""

    def __init__(self, labels):
        self.labels = labels
        self.active = 0
        self.hover = -1
        self.palette_idx = 0
        self.palettes = [
            {
                "name": "Azul Classico",
                "bar_bg": (10, 42, 94),
                "tab_normal": (18, 72, 145),
                "tab_hover": (28, 98, 182),
                "tab_active": (70, 150, 240),
                "tab_border": (150, 198, 255),
                "tab_text": (235, 245, 255),
            },
            {
                "name": "Azul Petroleo",
                "bar_bg": (14, 36, 58),
                "tab_normal": (24, 62, 96),
                "tab_hover": (36, 82, 124),
                "tab_active": (64, 122, 182),
                "tab_border": (133, 186, 230),
                "tab_text": (236, 244, 250),
            },
            {
                "name": "Cinza Azulado",
                "bar_bg": (30, 44, 62),
                "tab_normal": (48, 68, 94),
                "tab_hover": (66, 90, 120),
                "tab_active": (98, 130, 168),
                "tab_border": (173, 198, 228),
                "tab_text": (240, 246, 252),
            },
        ]

    def active_label(self) -> str:
        return self.labels[self.active]

    def next_palette(self):
        self.palette_idx = (self.palette_idx + 1) % len(self.palettes)

    def current_palette_name(self) -> str:
        return self.palettes[self.palette_idx]["name"]

    def _bar_rect(self):
        x = cfg.SIDE_W + 290
        y = 5
        h = max(24, cfg.TOP_BAR_H - 10)
        right_reserved = 260
        w = max(260, cfg.WIDTH - x - right_reserved)
        return pygame.Rect(x, y, w, h)

    def _tab_rects(self):
        bar = self._bar_rect()
        gap = 6
        n = len(self.labels)
        tab_w = max(90, (bar.w - gap * (n - 1)) // n)
        rects = []
        x = bar.x
        for _ in self.labels:
            rects.append(pygame.Rect(x, bar.y + 1, tab_w, bar.h - 2))
            x += tab_w + gap
        return rects, bar

    def handle_mouse_move(self, pos):
        self.hover = -1
        rects, _ = self._tab_rects()
        for i, r in enumerate(rects):
            if r.collidepoint(pos):
                self.hover = i
                break

    def handle_mouse_down(self, pos) -> bool:
        rects, _ = self._tab_rects()
        for i, r in enumerate(rects):
            if r.collidepoint(pos):
                if i != self.active:
                    self.active = i
                    return True
                return False
        return False

    def draw(self, surface, fonts):
        fn_tab = fonts["tab"]
        rects, bar = self._tab_rects()
        pal = self.palettes[self.palette_idx]
        bar_bg = pal["bar_bg"]
        tab_normal = pal["tab_normal"]
        tab_hover = pal["tab_hover"]
        tab_active = pal["tab_active"]
        tab_border = pal["tab_border"]
        tab_text = pal["tab_text"]
        pygame.draw.rect(surface, bar_bg, bar, border_radius=4)

        for i, (r, label) in enumerate(zip(rects, self.labels)):
            is_active = i == self.active
            is_hover = i == self.hover and not is_active

            if is_active:
                fill = tab_active
            elif is_hover:
                fill = tab_hover
            else:
                fill = tab_normal

            pygame.draw.rect(surface, fill, r, border_radius=3)
            pygame.draw.rect(surface, tab_border, r, 1, border_radius=3)

            t = fn_tab.render(label, True, tab_text)
            surface.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))


def _draw_topbar(surface, fonts, fps: float, current_exemplo, menu_aulas: MenuAulasTopbar):
    r = pygame.Rect(0, 0, cfg.WIDTH, cfg.TOP_BAR_H)
    pygame.draw.rect(surface, cfg.BG2, r)
    pygame.draw.line(surface, cfg.BORDER, (0, cfg.TOP_BAR_H - 1), (cfg.WIDTH, cfg.TOP_BAR_H - 1), 1)

    fn_hd = fonts["hd"]
    fn_sm = fonts["sm"]

    title = cfg.APP_TITLE
    s = fn_hd.render(title, True, cfg.WHITE)
    surface.blit(s, (cfg.SIDE_W + 12, cfg.TOP_BAR_H // 2 - s.get_height() // 2))

    if current_exemplo:
        ex_lbl = fn_sm.render(f"|  {current_exemplo.NAME}", True, cfg.GRAY)
        surface.blit(ex_lbl, (cfg.SIDE_W + 12 + s.get_width() + 6, cfg.TOP_BAR_H // 2 - ex_lbl.get_height() // 2))

    menu_aulas.draw(surface, fonts)

    fps_s = fn_sm.render(f"FPS {fps:.0f}", True, cfg.GRAY2)
    surface.blit(fps_s, (cfg.WIDTH - fps_s.get_width() - 10, cfg.TOP_BAR_H // 2 - fps_s.get_height() // 2))

    theme_s = fn_sm.render(f"Tema: {cfg.current_theme()} | Paleta: {menu_aulas.current_palette_name()}", True, cfg.GRAY2)
    surface.blit(
        theme_s,
        (
            cfg.WIDTH - fps_s.get_width() - theme_s.get_width() - 30,
            cfg.TOP_BAR_H // 2 - theme_s.get_height() // 2,
        ),
    )


def _draw_footer(surface, fonts):
    fy = cfg.HEIGHT - cfg.FOOTER_H
    pygame.draw.rect(surface, cfg.BG2, (0, fy, cfg.WIDTH, cfg.FOOTER_H))
    pygame.draw.line(surface, cfg.BORDER, (0, fy), (cfg.WIDTH, fy), 1)
    s = fonts["sm"].render(cfg.FOOTER_TEXT, True, cfg.GRAY2)
    surface.blit(s, (cfg.SIDE_W + 8, fy + (cfg.FOOTER_H - s.get_height()) // 2))

    atalhos = "[ESP] Animar   [R] Reset   [UP/DOWN/LEFT/RIGHT] Ajustar   [T] Tema   [V] Paleta"
    sa = fonts["sm"].render(atalhos, True, cfg.GRAY2)
    surface.blit(sa, (cfg.WIDTH - sa.get_width() - 8, fy + (cfg.FOOTER_H - sa.get_height()) // 2))


def main():
    pygame.init()
    pygame.display.set_caption(cfg.APP_TITLE)

    flags = pygame.RESIZABLE
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT), flags)
    clock = pygame.time.Clock()
    fonts = _build_fonts()

    menu_aulas = MenuAulasTopbar(AULAS)
    sidebar = SidebarProgramas(PROGRAMAS_POR_AULA[menu_aulas.active_label()], _split_indices_for_aula(menu_aulas.active_label()))
    handler = InputHandler()
    keymap = KeyMap.default()

    _instances: dict[type, object] = {}

    def get_exemplo():
        cls = sidebar.active_class()
        if cls is None:
            return None
        if cls not in _instances:
            _instances[cls] = cls()
        return _instances[cls]

    running = True

    def on_quit():
        nonlocal running
        running = False

    def on_resize(w, h):
        nonlocal screen
        cfg.WIDTH = max(800, w)
        cfg.HEIGHT = max(480, h)
        cfg.update_layout()
        screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT), flags)
        for ex in _instances.values():
            if hasattr(ex, "reset_windows"):
                ex.reset_windows()

    def on_key(key, mod):
        ex = get_exemplo()

        if key == pygame.K_t:
            themes = list(cfg.THEMES.keys())
            idx = themes.index(cfg.current_theme())
            cfg.apply_theme(themes[(idx + 1) % len(themes)])
            return

        if key == pygame.K_v:
            menu_aulas.next_palette()
            return

        if ex and hasattr(ex, "handle_extra"):
            ex.handle_extra(key)

        action = keymap.get(key)
        if action and ex:
            ex.handle_action(action)

    def on_mouse_down(pos, button):
        if button != 1:
            return

        if menu_aulas.handle_mouse_down(pos):
            sidebar.set_items(PROGRAMAS_POR_AULA[menu_aulas.active_label()], _split_indices_for_aula(menu_aulas.active_label()))
            return

        if pos[0] < cfg.SIDE_W and sidebar.handle_mouse_down(pos):
            return

        ex = get_exemplo()
        if ex and hasattr(ex, "handle_mouse_down"):
            ex.handle_mouse_down(pos)

    def on_mouse_move(pos, rel):
        menu_aulas.handle_mouse_move(pos)
        sidebar.handle_mouse_move(pos)
        ex = get_exemplo()
        if ex and hasattr(ex, "handle_mouse_move"):
            ex.handle_mouse_move(pos)

    def on_mouse_up(pos, button):
        ex = get_exemplo()
        if ex and hasattr(ex, "handle_mouse_up"):
            ex.handle_mouse_up(pos)

    def on_scroll(x, dy):
        ex = get_exemplo()
        if ex and hasattr(ex, "handle_scroll"):
            ex.handle_scroll(dy)

    handler.on("on_quit", on_quit)
    handler.on("on_resize", on_resize)
    handler.on("on_key", on_key)
    handler.on("on_mouse_down", on_mouse_down)
    handler.on("on_mouse_move", on_mouse_move)
    handler.on("on_mouse_up", on_mouse_up)
    handler.on("on_scroll", on_scroll)

    while running:
        dt = clock.tick(cfg.FPS) / 1000.0

        events = pygame.event.get()
        if not handler.process(events):
            break

        ex = get_exemplo()

        if ex:
            ex.update(dt)

        screen.fill(cfg.BG)

        cx, cy, cw, ch = cfg.canvas_rect()
        pygame.draw.rect(screen, cfg.BG, (cx, cy, cw, ch))

        if ex:
            ex.draw(screen, fonts)
        else:
            if sidebar.has_items():
                msg = fonts["lg"].render("Selecione um programa no menu esquerdo", True, cfg.GRAY)
            else:
                msg = fonts["lg"].render(f"Nenhum programa cadastrado para {menu_aulas.active_label()}", True, cfg.GRAY)
            screen.blit(msg, (cx + cw // 2 - msg.get_width() // 2, cy + ch // 2 - msg.get_height() // 2))

        sidebar.draw(screen, fonts, menu_aulas.active_label())
        _draw_topbar(screen, fonts, clock.get_fps(), ex, menu_aulas)
        _draw_footer(screen, fonts)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()




















