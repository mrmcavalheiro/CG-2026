"""
============================================================
 input/handler.py
 Centraliza todo o tratamento de eventos de teclado e mouse.
 O App apenas chama handler.process(events) a cada frame.
============================================================
"""

import pygame


class InputHandler:
    """
    Processa a fila de eventos do pygame e despacha para
    os callbacks registrados.

    Callbacks disponíveis (todos opcionais):
      on_quit()
      on_key(key, mod)          ← tecla pressionada
      on_key_up(key, mod)       ← tecla solta
      on_mouse_move(pos, rel)
      on_mouse_down(pos, button)
      on_mouse_up(pos, button)
      on_scroll(x, y)           ← scroll do mouse (wheel)
    """

    def __init__(self):
        self._callbacks = {}

    # ── REGISTRO ──────────────────────────────
    def on(self, event_name: str, fn):
        """Registra um callback para um tipo de evento."""
        self._callbacks[event_name] = fn
        return self   # permite encadeamento

    def _fire(self, name, *args):
        fn = self._callbacks.get(name)
        if fn:
            fn(*args)

    # ── PROCESSAMENTO ─────────────────────────
    def process(self, events):
        """
        Chama com pygame.event.get() a cada frame.
        Retorna False se o app deve fechar.
        """
        for event in events:

            if event.type == pygame.QUIT:
                self._fire('on_quit')
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._fire('on_quit')
                    return False
                self._fire('on_key', event.key, event.mod)

            elif event.type == pygame.KEYUP:
                self._fire('on_key_up', event.key, event.mod)

            elif event.type == pygame.MOUSEMOTION:
                self._fire('on_mouse_move', event.pos, event.rel)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Botões 4/5 (scroll legado Pygame 1.x) REMOVIDOS para evitar
                # duplo disparo com MOUSEWHEEL (Pygame 2.x). Usar apenas MOUSEWHEEL.
                self._fire('on_mouse_down', event.pos, event.button)

            elif event.type == pygame.MOUSEBUTTONUP:
                self._fire('on_mouse_up', event.pos, event.button)

            elif event.type == pygame.MOUSEWHEEL:
                self._fire('on_scroll', event.x, event.y)

            elif event.type == pygame.VIDEORESIZE:
                self._fire('on_resize', event.w, event.h)

            elif event.type == pygame.WINDOWRESIZED:
                # Pygame 2.x usa WINDOWRESIZED em vez de VIDEORESIZE
                self._fire('on_resize', event.x, event.y)

        return True


# ─────────────────────────────────────────────
#  ATALHOS DE TECLADO GLOBAIS
# ─────────────────────────────────────────────
class KeyMap:
    """
    Mapa simples de tecla → ação nomeada.
    Permite configurar atalhos sem hardcodar teclas
    nos exemplos.

    Uso:
        km = KeyMap()
        km.bind(pygame.K_SPACE, 'toggle_anim')
        km.bind(pygame.K_r,     'reset')
        ...
        action = km.get(key)   # retorna str ou None
    """

    def __init__(self):
        self._map: dict[int, str] = {}

    def bind(self, key: int, action: str):
        self._map[key] = action
        return self

    def get(self, key: int) -> str | None:
        return self._map.get(key)

    @staticmethod
    def default():
        """Mapa padrão para os exemplos."""
        km = KeyMap()
        km.bind(pygame.K_SPACE,  'toggle_anim')
        km.bind(pygame.K_r,      'reset')
        km.bind(pygame.K_UP,     'inc')
        km.bind(pygame.K_DOWN,   'dec')
        km.bind(pygame.K_LEFT,   'dec_alt')
        km.bind(pygame.K_RIGHT,  'inc_alt')
        return km
