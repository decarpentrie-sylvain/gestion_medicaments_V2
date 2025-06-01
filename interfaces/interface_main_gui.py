import tkinter as tk
import sqlite3
from tkinter import ttk
from tkinter import messagebox

from interfaces.import_frame import ImportFrame
from interfaces.catalogue_frame import CatalogueFrame
from interfaces.validation_frame import ValidationFrame
from interfaces.stock_frame import StockFrame

from modules.gestion_audit import DB_PATH

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion Médicaments")
        self.root.geometry("1200x700")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Onglets de base
        self.import_tab = ImportFrame(self.notebook)
        self.notebook.add(self.import_tab, text="📥 Import")

        self.catalogue_tab = CatalogueFrame(self.notebook)
        self.notebook.add(self.catalogue_tab, text="💊 Catalogue")

        self.stock_tab = StockFrame(self.notebook)
        self.notebook.add(self.stock_tab, text="📦 Stock")

        self.validation_tab = ValidationFrame(self.notebook)
        self.notebook.add(self.validation_tab, text="✅ Validation")

        # Onglet Admin (désactivé par défaut ; activé pour "admin")
        self.admin_tab = ttk.Frame(self.notebook)
        btn_clear = ttk.Button(self.admin_tab, text="🗑️ Vider la base", command=self.clear_database)
        btn_clear.pack(pady=20)
        self.notebook.add(self.admin_tab, text="🛠️ Admin", state="disabled")

        # Quand on se connectera, on appellera self._on_user_login(nom_utilisateur)
        # pour activer/désactiver l’onglet Admin.
        # ImportFrame doit appeler self.master._on_user_login après login réussi.
        self.import_tab.on_login = self._on_user_login

    def _on_user_login(self, username):
        """
        Active l’onglet Admin seulement si l’utilisateur est 'admin'
        (pour l’instant, on autorise uniquement 'admin'; plus tard, on peut
        avoir une table rôles ou ’is_admin’ en DB).
        """
        if username == "admin":
            self.notebook.tab(self.admin_tab, state="normal")
        else:
            self.notebook.tab(self.admin_tab, state="disabled")

    def clear_database(self):
        # Exemple de méthode pour vider les tables
        resp = messagebox.askyesno("Vider la base", "Voulez-vous vraiment tout supprimer ?")
        if not resp:
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # Supprime références avant medicaments et fournisseurs
        cur.execute("DELETE FROM references_fournisseurs")
        cur.execute("DELETE FROM medicaments")
        cur.execute("DELETE FROM fournisseurs")
        # Vous pouvez aussi vider utilisateurs/journal si besoin
        conn.commit()
        conn.execute("VACUUM")
        conn.close()
        messagebox.showinfo("Base vidée", "Toutes les données ont été supprimées.")
        # Vous pouvez forcer un rechargement du catalogue ici si besoin.
