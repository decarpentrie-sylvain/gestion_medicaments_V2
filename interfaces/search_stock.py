

import tkinter as tk
from tkinter import ttk

class SearchStockWindow(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("🔎 Recherche multicritère")
        self.geometry("500x400")
        self.callback = callback  # fonction à appeler avec les filtres

        # Champ : nom contient
        tk.Label(self, text="Nom contient :").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.nom_var = tk.StringVar()
        tk.Entry(self, textvariable=self.nom_var).grid(row=0, column=1, sticky="ew", padx=10)

        # Champ : fournisseur contient
        tk.Label(self, text="Fournisseur contient :").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.fournisseur_var = tk.StringVar()
        tk.Entry(self, textvariable=self.fournisseur_var).grid(row=1, column=1, sticky="ew", padx=10)

        # Champ : rupture (0/1)
        tk.Label(self, text="Rupture (0/1) :").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.rupture_var = tk.StringVar()
        tk.Entry(self, textvariable=self.rupture_var).grid(row=2, column=1, sticky="ew", padx=10)

        # Bouton Rechercher
        bouton = tk.Button(self, text="Rechercher", command=self.valider)
        bouton.grid(row=10, column=0, columnspan=2, pady=20)

        self.columnconfigure(1, weight=1)

    def valider(self):
        filtres = {
            "nom": self.nom_var.get(),
            "code_fournisseur": self.fournisseur_var.get(),
            "en_rupture": self.rupture_var.get()
        }
        self.callback(filtres)
        self.destroy()