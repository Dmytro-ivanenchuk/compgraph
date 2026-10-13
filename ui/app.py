import tkinter as tk
from tkinter import ttk

from curves.strophoid import Strophoid
from scene.curve_scene import CurveScene
from services.report import CalculationReport
from ui.canvas_view import CanvasView
from ui.panels.animation_panel import AnimationPanel
from ui.panels.base import Callbacks
from ui.panels.curve_panel import CurvePanel
from ui.panels.info_panel import InfoPanel
from ui.panels.transform_panel import TransformPanel
from view.options import DisplayOptions

HINT = "ЛКМ — центр C   |   ПКМ — рух   |   колесо — масштаб"


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Лабораторна робота №2 — Строфоїда")
        root.geometry("1280x820")
        root.minsize(900, 620)

        # модель
        self.scene = CurveScene(Strophoid(2.0))
        self.options = DisplayOptions()
        self.report = CalculationReport(self.scene)

        # каркас вікна
        left = ttk.Frame(root, padding=6)
        left.pack(side="left", fill="y")
        right = ttk.Frame(root)
        right.pack(side="left", fill="both", expand=True)

        self.canvas = CanvasView(right, self.scene, self.options,
                                 on_pick=self._on_pick, on_hover=self._on_hover)
        self.canvas.pack(fill="both", expand=True)
        self.status = ttk.Label(right, anchor="w", padding=(8, 3))
        self.status.pack(fill="x")

        # панелі
        cb = Callbacks(refresh=self.refresh, redraw=self.canvas.request_redraw, status=self.set_status)
        nb = ttk.Notebook(left)
        nb.pack(fill="x")
        self.curve_panel = CurvePanel(nb, self.scene, self.options, cb)
        self.transform_panel = TransformPanel(nb, self.scene, cb)
        self.animation_panel = AnimationPanel(nb, self.scene, cb)
        nb.add(self.curve_panel, text="Крива")
        nb.add(self.transform_panel, text="Перетворення")
        nb.add(self.animation_panel, text="Анімація")
        self.info_panel = InfoPanel(left)
        self.info_panel.pack(fill="both", expand=True, pady=(8, 0))

        self.set_status()
        self.refresh()

    # ------------------------------------------------------------------
    def refresh(self):
        """Стан сцени змінився: оновити повзунки, розрахунки та малюнок."""
        self.curve_panel.sync_from_scene()
        self.info_panel.show(self.report.text())
        self.canvas.request_redraw()

    def set_status(self, text=None):
        self.status.config(text=f"{text}     {HINT}" if text else HINT)

    def _on_pick(self, x, y):
        self.scene.set_center(x, y)
        self.transform_panel.load_center()
        self.canvas.request_redraw()

    def _on_hover(self, x, y):
        self.set_status(f"x = {x:.2f},  y = {y:.2f}")
