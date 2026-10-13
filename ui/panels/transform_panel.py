"""Вкладка «Перетворення»: центр C, зсув, обертання (евклідові перетворення)."""

from tkinter import ttk

from ui.forms import NumberForm, action_button
from ui.panels.base import Panel


class TransformPanel(Panel):
    def __init__(self, parent, scene, callbacks):
        super().__init__(parent, scene, callbacks)
        self._build()

    def _build(self):
        lf = ttk.LabelFrame(self, text="Центр C (клік ЛКМ на сцені)", padding=6)
        lf.pack(fill="x")
        self.center_form = NumberForm(lf)
        self.center_form.row(0, "C (x, y)", [("cx", self.scene.center[0]), ("cy", self.scene.center[1])])
        self.center_form.on_edit("cx", self._on_center_typed)
        self.center_form.on_edit("cy", self._on_center_typed)

        lf = ttk.LabelFrame(self, text="Евклідові", padding=6)
        lf.pack(fill="x", pady=(8, 0))
        self.form = NumberForm(lf)
        self.form.row(0, "Зсув (dx, dy)", [("dx", 1), ("dy", 1)])
        action_button(lf, 1, "Зсунути", self.guarded(self.shift))
        self.form.row(2, "Кут, °", [("angle", 30)])
        action_button(lf, 3, "Обернути навколо C", self.guarded(self.rotate))

        ttk.Button(self, text="Скинути перетворення", command=self.reset).pack(fill="x", pady=(8, 0))

    # ------------------------------------------------------------------
    def load_center(self):
        """Показати в полях центр, обраний кліком на сцені."""
        x, y = self.scene.center
        self.center_form.set("cx", f"{x:.2f}")
        self.center_form.set("cy", f"{y:.2f}")

    def _on_center_typed(self):
        try:
            self.scene.set_center(*self.center_form.get_all("cx", "cy"))
        except ValueError:
            return                       # поле ще не дописано
        self.cb.redraw()

    def shift(self):
        dx, dy = self.form.get_all("dx", "dy")
        self.scene.shift(dx, dy)
        self.cb.refresh()

    def rotate(self):
        cx, cy = self.center_form.get_all("cx", "cy")
        angle = self.form.get("angle")
        self.scene.set_center(cx, cy)
        self.scene.rotate(cx, cy, angle)
        self.cb.refresh()

    def reset(self):
        self.scene.reset_transform()
        self.cb.refresh()
