"""Допоміжні елементи форм: числові поля та кнопки."""

import tkinter as tk
from tkinter import ttk


class NumberForm:
    """Набір підписаних числових полів у grid-контейнері."""

    def __init__(self, parent):
        self.parent = parent
        self._vars = {}
        self._entries = {}

    def row(self, row, label, fields, width=8):
        """fields = [(ключ, значення за замовчуванням), ...]"""
        ttk.Label(self.parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        for j, (key, default) in enumerate(fields):
            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(self.parent, textvariable=var, width=width)
            entry.grid(row=row, column=j + 1, padx=2)
            self._vars[key] = var
            self._entries[key] = entry

    def get(self, key) -> float:
        """Число з поля; ValueError, якщо введено не число."""
        return float(self._vars[key].get().strip().replace(",", "."))

    def get_all(self, *keys):
        return [self.get(k) for k in keys]

    def set(self, key, value):
        self._vars[key].set(value)

    def on_edit(self, key, callback):
        self._entries[key].bind("<KeyRelease>", lambda e: callback())


def action_button(parent, row, text, command, span=4):
    btn = ttk.Button(parent, text=text, command=command)
    btn.grid(row=row, column=0, columnspan=span, sticky="ew", pady=(2, 6))
    return btn
