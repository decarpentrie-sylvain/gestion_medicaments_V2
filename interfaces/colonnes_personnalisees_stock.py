import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

class DragListbox(tk.Listbox):
    def __init__(self, master, items, selected_items, **kwargs):
        super().__init__(master, selectmode=tk.MULTIPLE, activestyle="none", **kwargs)
        self.items = items
        self.selected_items = selected_items
        self.insert_items()
        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<ButtonRelease-1>", self.drop)
        self.curIndex = None

    def insert_items(self):
        self.delete(0, tk.END)
        for item in self.items:
            self.insert(tk.END, item)
        # Sélectionner les éléments actifs
        for i, item in enumerate(self.items):
            if item in self.selected_items:
                self.selection_set(i)

    def click(self, event):
        self.curIndex = self.nearest(event.y)

    def drag(self, event):
        i = self.nearest(event.y)
        if i != self.curIndex:
            self.items[self.curIndex], self.items[i] = self.items[i], self.items[self.curIndex]
            self.insert_items()
            self.curIndex = i

    def drop(self, event):
        self.curIndex = None

    def get_ordered_selection(self):
        return [self.items[i] for i in self.curselection()]

class ColonnesStockWindow(tk.Toplevel):
    def __init__(self, master, colonnes_disponibles, colonnes_actives, callback):
        super().__init__(master)
        self.title("Colonnes à afficher (Vue personnalisée)")
        self.geometry("500x600")
        self.callback = callback
        self.vars = {}

        # Scrollbar verticale
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.drag_listbox = DragListbox(scrollable_frame, colonnes_disponibles, colonnes_actives, height=25)
        self.drag_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Bouton Valider
        btn = tk.Button(self, text="Valider", command=self.valider)
        btn.pack(pady=10)

    def valider(self):
        selection = self.drag_listbox.get_ordered_selection()
        self.callback(selection)
        self.destroy()