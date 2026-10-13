"""Базова панель керування."""

from dataclasses import dataclass
from tkinter import ttk
from typing import Callable

from services.errors import ValidationError


@dataclass
class Callbacks:
    """Що панель може попросити в застосунку (панелі не знають одна про одну)."""
    refresh: Callable[[], None]       # перерахувати розрахунки та перемалювати
    redraw: Callable[[], None]        # лише перемалювати
    status: Callable[[str], None]     # повідомлення у рядку стану


class Panel(ttk.Frame):
    def __init__(self, parent, scene, callbacks: Callbacks):
        super().__init__(parent, padding=6)
        self.scene = scene
        self.cb = callbacks

    def guarded(self, fn):
        """Обгортка для обробників: помилки вводу -> повідомлення в рядку стану."""
        def run():
            try:
                fn()
            except ValidationError as e:
                self.cb.status(str(e))
            except ValueError:
                self.cb.status("Помилка: введіть коректні числа")
        return run
