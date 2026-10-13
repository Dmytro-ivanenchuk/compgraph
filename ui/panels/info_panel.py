"""Панель «Розрахунки»."""

import tkinter as tk
from tkinter import ttk


class InfoPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Розрахунки", padding=4)
        self.text = tk.Text(self, height=22, width=48, font=("Courier", 9), bg="#f4f4f4",
                            relief="flat", state="disabled", wrap="none")
        self.text.pack(fill="both", expand=True)

    def show(self, content: str):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.config(state="disabled")
