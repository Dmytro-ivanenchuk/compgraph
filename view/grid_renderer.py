"""Сітка, осі та цифри. Перемальовується лише коли змінився вигляд."""

import math

from view import theme


class GridRenderer:
    TAG = "grid"

    def __init__(self, canvas):
        self.canvas = canvas
        self._key = None

    def draw(self, vp):
        key = vp.key()
        if key == self._key:
            return
        self.canvas.delete(self.TAG)
        self._draw(vp)
        self.canvas.tag_lower(self.TAG)   # під усіма динамічними об'єктами
        self._key = key

    # ------------------------------------------------------------------
    def _line(self, *args, **kw):
        self.canvas.create_line(*args, tags=self.TAG, **kw)

    def _text(self, *args, **kw):
        self.canvas.create_text(*args, tags=self.TAG, **kw)

    def _draw(self, vp):
        z, ox, oy, w, h = vp.zoom, vp.ox, vp.oy, vp.width, vp.height
        step = next((v for v in theme.NICE_STEPS if v * z >= 18), theme.NICE_STEPS[-1])  # лінії
        lab = next((v for v in theme.NICE_STEPS if v * z >= 55), theme.NICE_STEPS[-1])   # підписи

        # лінії сітки (кожна 5-та виразніша)
        for i in range(int(math.floor(-ox / z / step)), int(math.ceil((w - ox) / z / step)) + 1):
            x = ox + i * step * z
            self._line(x, 0, x, h, fill=theme.GRID_MAJOR if i % 5 == 0 else theme.GRID_MINOR)
        for j in range(int(math.floor((oy - h) / z / step)), int(math.ceil(oy / z / step)) + 1):
            y = oy - j * step * z
            self._line(0, y, w, y, fill=theme.GRID_MAJOR if j % 5 == 0 else theme.GRID_MINOR)

        # осі зі стрілками
        x_axis = 0 <= oy <= h
        y_axis = 0 <= ox <= w
        if x_axis:
            self._line(0, oy, w - 4, oy, fill=theme.AXIS, width=2, arrow="last", arrowshape=(10, 12, 4))
        if y_axis:
            self._line(ox, h, ox, 4, fill=theme.AXIS, width=2, arrow="last", arrowshape=(10, 12, 4))

        # цифри (прилипають до краю вікна, якщо вісь поза екраном)
        ly = min(max(oy + 5, 2), h - 16)
        lx = min(max(ox - 7, 30), w - 4)
        for k in range(int(math.floor(-ox / z / lab)), int(math.ceil((w - ox) / z / lab)) + 1):
            if k == 0:
                continue
            x = ox + k * lab * z
            if x_axis:
                self._line(x, oy - 3, x, oy + 3, fill=theme.AXIS)
            self._text(x, ly, text=f"{round(k * lab, 6):g}", anchor="n", font=theme.FONT, fill=theme.TEXT)
        for k in range(int(math.floor((oy - h) / z / lab)), int(math.ceil(oy / z / lab)) + 1):
            if k == 0:
                continue
            y = oy - k * lab * z
            if y_axis:
                self._line(ox - 3, y, ox + 3, y, fill=theme.AXIS)
            self._text(lx, y, text=f"{round(k * lab, 6):g}", anchor="e", font=theme.FONT, fill=theme.TEXT)
        if x_axis and y_axis:
            self._text(ox - 6, oy + 6, text="0", anchor="ne", font=theme.FONT, fill=theme.TEXT)

        # назви осей
        self._text(w - 14, min(max(oy - 14, 14), h - 14), text="x", font=theme.FONT_AXIS, fill=theme.AXIS)
        self._text(min(max(ox + 14, 14), w - 14), 14, text="y", font=theme.FONT_AXIS, fill=theme.AXIS)
