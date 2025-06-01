import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path
from modules.gestion_audit import log_action

DB_PATH = Path("db/base_stock.sqlite")

class CatalogueFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        btn_refresh = ttk.Button(self, text="🔄 Recharger Catalogue", command=self.charger_catalogue)
        btn_refresh.pack(pady=5)

        colonnes = ("ID Ref", "Nom Médicament", "Fournisseur", "CIP", "GTIN", "Code FR", "Prix", "Par lot", "Dernier import")
        self.tree = ttk.Treeview(self, columns=colonnes, show="headings")
        for col in colonnes:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.charger_catalogue()

    def charger_catalogue(self):
        # Vide le Treeview
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                SELECT
                  rf.id,
                  m.nom,
                  f.nom,
                  rf.code_cip,
                  rf.code_gtin,
                  rf.code_fournisseur,
                  rf.tarif_unitaire,
                  rf.par_lot_de,
                  rf.date_import
                FROM references_fournisseurs rf
                JOIN medicaments m ON rf.id_medicament = m.id
                JOIN fournisseurs f ON rf.fournisseur_id = f.id
                ORDER BY m.nom, f.nom
            """)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)
            conn.close()
            log_action("reload_catalogue", "Catalogue rechargé", utilisateur="admin")
        except Exception as e:
            messagebox.showerror("Erreur Catalogue", str(e))