"""Полотно: вигляд, миша (панорама, зум, вибір центра) і запуск рендерерів."""

import tkinter as tk

from view import theme
from view.grid_renderer import GridRenderer
from view.scene_renderer import SceneRenderer
from view.viewport import Viewport


class CanvasView(tk.Canvas):
    def __init__(self, parent, scene, options, on_pick, on_hover):
        super().__init__(parent, bg=theme.BG, highlightthickness=0)
        self.scene = scene
        self.options = options
        self.on_pick = on_pick          # (x, y) -- ЛКМ: світові координати
        self.on_hover = on_hover        # (x, y) -- рух миші

        self.viewport = Viewport()
        self.grid_renderer = GridRenderer(self)
        self.scene_renderer = SceneRenderer(self)
        self._pending = False
        self._pan = None

        self.bind("<Configure>", self._on_configure)
        self.bind("<Button-1>", self._on_left_click)
        self.bind("<Motion>", self._on_motion)
        for b in ("2", "3"):             # права кнопка (на macOS -- Button-2) та середня
            self.bind(f"<ButtonPress-{b}>", self._pan_start)
            self.bind(f"<B{b}-Motion>", self._pan_move)
            self.bind(f"<ButtonRelease-{b}>", self._pan_end)
        self.bind("<MouseWheel>", self._on_wheel)
        self.bind("<Button-4>", self._on_wheel)   # Linux
        self.bind("<Button-5>", self._on_wheel)

    # ------------------------------------------------------------------
    # Перемальовування (кілька запитів за один цикл подій зливаються в один)
    # ------------------------------------------------------------------
    def request_redraw(self):
        if not self._pending:
            self._pending = True
            self.after_idle(self._redraw)

    def _redraw(self):
        self._pending = False
        vp = self.viewport
        if vp.width < 10 or vp.height < 10:
            return
        self.grid_renderer.draw(vp)
        self.scene_renderer.draw(self.scene, vp, self.options)

    # ------------------------------------------------------------------
    # Миша
    # ------------------------------------------------------------------
    def _on_configure(self, e):
        self.viewport.resize(e.width, e.height)
        self.request_redraw()

    def _on_left_click(self, e):
        self.on_pick(*self.viewport.to_world(e.x, e.y))

    def _on_motion(self, e):
        self.on_hover(*self.viewport.to_world(e.x, e.y))

    def _pan_start(self, e):
        vp = self.viewport
        self._pan = (e.x, e.y, vp.ox, vp.oy)
        self.config(cursor="fleur")

    def _pan_move(self, e):
        if self._pan is None:
            return
        x0, y0, ox, oy = self._pan
        self.viewport.ox = ox + (e.x - x0)
        self.viewport.oy = oy + (e.y - y0)
        self.request_redraw()

    def _pan_end(self, e):
        self._pan = None
        self.config(cursor="")

    def _on_wheel(self, e):
        if e.num == 4 or e.delta > 0:
            factor = 1.1
        elif e.num == 5 or e.delta < 0:
            factor = 1 / 1.1
        else:
            return
        self.viewport.zoom_at(factor, e.x, e.y)
        self.request_redraw()
