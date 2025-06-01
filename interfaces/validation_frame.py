import tkinter as tk
from tkinter import ttk, messagebox

class ValidationFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ttk.Label(self, text="Module de validation (à implémenter)")
        label.pack(pady=20)