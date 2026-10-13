"""Вкладка «Анімація»: запуск/зупинка, межі та крок параметра a."""

import tkinter as tk
from tkinter import ttk

from services.animator import Animator
from services.errors import ValidationError
from ui.forms import NumberForm
from ui.panels.base import Panel


class AnimationPanel(Panel):
    def __init__(self, parent, scene, callbacks):
        super().__init__(parent, scene, callbacks)
        self.animator = Animator()
        self._job = None            # id запланованого кадру
        self._interval = 20
        self._move_point = tk.BooleanVar(value=False)
        self._build()

    def _build(self):
        lf = ttk.LabelFrame(self, text="Зміна параметра a", padding=6)
        lf.pack(fill="x")
        self.form = NumberForm(lf)
        self.form.row(0, "a мін, макс", [("a_min", 1), ("a_max", 6)])
        self.form.row(1, "Крок a", [("a_step", 0.05)])
        self.form.row(2, "Кадр, мс", [("a_ms", 20)])
        ttk.Checkbutton(lf, text="Рухати також точку дотику", variable=self._move_point).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(4, 0))
        self.button = ttk.Button(lf, text="▶ Старт", command=self.guarded(self.toggle))
        self.button.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(6, 0))

    @property
    def running(self) -> bool:
        return self._job is not None

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        lo, hi, step, ms = self.form.get_all("a_min", "a_max", "a_step", "a_ms")
        if ms < 5:
            raise ValidationError("Анімація: кадр має бути не менше 5 мс")
        self.animator.configure(self.scene, lo, hi, step, self._move_point.get())
        self._interval = int(ms)
        self.button.config(text="■ Стоп")
        self._job = self.after(self._interval, self._tick)

    def stop(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        self.button.config(text="▶ Старт")

    def _tick(self):
        if self._job is None:
            return
        self.animator.advance(self.scene)
        self.cb.refresh()
        self._job = self.after(self._interval, self._tick)
