import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

from interfaces.import_frame import ImportFrame
from interfaces.catalogue_frame import CatalogueFrame
from interfaces.validation_frame import ValidationFrame
from interfaces.stock_frame import StockFrame

from modules.gestion_audit import DB_PATH

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion des Médicaments")
        self.geometry("1200x800")

        # Création du Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Onglet Import
        self.import_tab = ImportFrame(self.notebook)
        self.notebook.add(self.import_tab, text="📥 Import")

        # Onglet Catalogue
        self.catalogue_tab = CatalogueFrame(self.notebook)
        self.notebook.add(self.catalogue_tab, text="💊 Catalogue")

        # Onglet Stock
        self.stock_tab = StockFrame(self.notebook)
        self.notebook.add(self.stock_tab, text="📦 Stock")

        # Onglet Validation
        self.validation_tab = ValidationFrame(self.notebook)
        self.notebook.add(self.validation_tab, text="✅ Validation")

        # Onglet Admin (désactivé par défaut)
        self.admin_tab = ttk.Frame(self.notebook)
        btn_clear = ttk.Button(self.admin_tab, text="🗑️ Vider la base", command=self.clear_database)
        btn_clear.pack(pady=20)
        self.notebook.add(self.admin_tab, text="🛠️ Admin", state="disabled")

        # Liaison du callback on_login
        self.import_tab.on_login = self._on_user_login

    def _on_user_login(self, username: str):
        if username == "admin":
            self.notebook.tab(self.admin_tab, state="normal")
        else:
            self.notebook.tab(self.admin_tab, state="disabled")

    def clear_database(self):
        resp = messagebox.askyesno("Vider la base", "Voulez-vous vraiment tout supprimer ?")
        if not resp:
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM references_fournisseurs")
        cur.execute("DELETE FROM medicaments")
        cur.execute("DELETE FROM fournisseurs")
        conn.commit()
        conn.close()
        messagebox.showinfo("Base vidée", "Toutes les données ont été supprimées.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
