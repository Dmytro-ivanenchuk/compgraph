"""Вкладка «Крива»: параметр a, точка φ, що показувати, довжина дуги."""

import tkinter as tk
from tkinter import ttk

from ui.forms import NumberForm, action_button
from ui.panels.base import Panel
from view.options import OPTION_LABELS


class CurvePanel(Panel):
    A_RESOLUTION = 0.05
    PHI_RESOLUTION = 0.5

    def __init__(self, parent, scene, options, callbacks):
        super().__init__(parent, scene, callbacks)
        self.options = options
        self._flag_vars = {}
        self._build()

    def _build(self):
        curve = self.scene.curve
        a_min, a_max = curve.A_RANGE
        phi_lim = curve.PHI_MAX - 0.9

        lf = ttk.LabelFrame(self, text="Параметри", padding=6)
        lf.pack(fill="x")
        ttk.Label(lf, text="a").grid(row=0, column=0, sticky="sw")
        self.a_scale = tk.Scale(lf, from_=a_min, to=a_max, resolution=self.A_RESOLUTION, orient="horizontal",
                                length=250, command=self._on_a)
        self.a_scale.set(curve.a)
        self.a_scale.grid(row=0, column=1)
        ttk.Label(lf, text="φ точки, °").grid(row=1, column=0, sticky="sw")
        self.phi_scale = tk.Scale(lf, from_=-phi_lim, to=phi_lim, resolution=self.PHI_RESOLUTION, orient="horizontal",
                                  length=250, command=self._on_phi)
        self.phi_scale.set(self.scene.phi)
        self.phi_scale.grid(row=1, column=1)

        lf = ttk.LabelFrame(self, text="Показувати", padding=6)
        lf.pack(fill="x", pady=(8, 0))
        for i, (field, label) in enumerate(OPTION_LABELS):
            var = tk.BooleanVar(value=getattr(self.options, field))
            self._flag_vars[field] = var
            ttk.Checkbutton(lf, text=label, variable=var, command=self._on_toggle).grid(
                row=i // 2, column=i % 2, sticky="w", padx=(0, 14))

        lf = ttk.LabelFrame(self, text="Довжина дуги", padding=6)
        lf.pack(fill="x", pady=(8, 0))
        self.arc_form = NumberForm(lf)
        self.arc_form.row(0, "φ₁, φ₂ (°)", [("arc1", self.scene.arc[0]), ("arc2", self.scene.arc[1])])
        action_button(lf, 1, "Обчислити", self.guarded(self._apply_arc))

    # ------------------------------------------------------------------
    def sync_from_scene(self):
        """Повзунки показують поточний стан (його може змінити, наприклад, анімація)."""
        if not self._is_echo(self.a_scale.get(), self.scene.curve.a, self.A_RESOLUTION):
            self.a_scale.set(self.scene.curve.a)
        if not self._is_echo(self.phi_scale.get(), self.scene.phi, self.PHI_RESOLUTION):
            self.phi_scale.set(self.scene.phi)

    @staticmethod
    def _is_echo(slider_value, state_value, resolution):
        """
        Tk викликає command повзунка і після програмного set(), причому з округленим
        до кроку значенням. Якщо повзунок відрізняється від стану менш ніж на пів кроку,
        це не дія користувача, а відлуння -- його не можна записувати назад у сцену.
        """
        return abs(float(slider_value) - state_value) <= resolution / 2 + 1e-9

    def _on_a(self, value):
        if self._is_echo(value, self.scene.curve.a, self.A_RESOLUTION):
            return
        self.scene.set_a(float(value))
        self.cb.refresh()

    def _on_phi(self, value):
        if self._is_echo(value, self.scene.phi, self.PHI_RESOLUTION):
            return
        self.scene.set_phi(float(value))
        self.cb.refresh()

    def _on_toggle(self):
        for field, var in self._flag_vars.items():
            setattr(self.options, field, var.get())
        self.cb.redraw()

    def _apply_arc(self):
        p1, p2 = self.arc_form.get_all("arc1", "arc2")
        self.scene.set_arc(p1, p2)
        self.cb.refresh()
