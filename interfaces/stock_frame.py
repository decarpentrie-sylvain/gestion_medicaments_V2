import tkinter as tk
from tkinter import ttk
from modules.gestion_audit import DB_PATH
from modules.bdd_utils import ajouter_colonnes_stock_complet as ajouter_colonnes_stock_complet_import

class StockFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Vérifier ou ajouter les colonnes manquantes dans la table 'medicaments'
        ajouter_colonnes_stock_complet_import(DB_PATH)

        # Titre
        titre = tk.Label(self, text="📦 Gestion du Stock de Médicaments", font=("Helvetica", 16, "bold"))
        titre.pack(pady=10)

        # Zone de recherche rapide
        recherche_frame = tk.Frame(self)
        recherche_frame.pack(pady=5)

        tk.Label(recherche_frame, text="Champ :").pack(side="left")
        self.champ_recherche = ttk.Combobox(recherche_frame, values=[
            "nom", "code_fournisseur", "code_cip", "code_gtin", "remplace_par"
        ])
        self.champ_recherche.set("nom")
        self.champ_recherche.pack(side="left", padx=5)

        tk.Label(recherche_frame, text="Contient :").pack(side="left")
        self.valeur_recherche = tk.StringVar()
        tk.Entry(recherche_frame, textvariable=self.valeur_recherche).pack(side="left", padx=5)

        tk.Button(recherche_frame, text="🔍 Recherche rapide", command=self.recherche_rapide).pack(side="left", padx=10)
        tk.Button(recherche_frame, text="🔎 Recherche multicritère", command=self.ouvrir_recherche_multicritere).pack(side="left", padx=10)
        tk.Button(recherche_frame, text="Afficher tous les médicaments", command=self.reinitialiser_filtres).pack(side="left", padx=10)
        tk.Button(recherche_frame, text="📤 Exporter la vue", command=self.exporter_vue_csv).pack(side="left", padx=10)
        self.label_filtres = tk.Label(recherche_frame, text="", fg="red", font=("Helvetica", 10, "bold"))
        self.label_filtres.pack(side="left", padx=10)

        # Choix de l'affichage des colonnes
        affichage_frame = tk.Frame(self)
        affichage_frame.pack(pady=(0, 5))

        tk.Label(affichage_frame, text="Affichage :").pack(side="left")
        self.mode_affichage = tk.StringVar(value="standard")

        self.bouton_modifier_colonnes = tk.Button(affichage_frame, text="🛠️ Modifier les colonnes affichées", command=self.ouvrir_fenetre_colonnes_personnalisees, state="disabled")
        self.bouton_modifier_colonnes.pack(side="left", padx=10)

        modes = [
            ("Minimal", "minimal"),
            ("Standard", "standard"),
            ("Personnalisé", "personnalise"),
            ("Complet (admin)", "complet")
        ]

        def on_select_mode_affichage(value):
            if value != "personnalise":
                # Fermer la fenêtre flottante si elle existe
                if hasattr(self, "fenetre_apercu") and self.fenetre_apercu.winfo_exists():
                    self.fenetre_apercu.destroy()
                    self._apercu_deja_affiche = False
                self.rafraichir_stock()
            else:
                self.ouvrir_fenetre_colonnes_personnalisees()

        for label, value in modes:
            etat = "normal" if value != "complet" else "disabled"
            bouton_radio = tk.Radiobutton(
                affichage_frame, text=label, variable=self.mode_affichage,
                value=value, state=etat, command=lambda v=value: on_select_mode_affichage(v)
            )
            bouton_radio.pack(side="left", padx=5)

        self.bouton_modifier_colonnes = tk.Button(affichage_frame, text="🛠️ Modifier les colonnes affichées", command=self.ouvrir_fenetre_colonnes_personnalisees)
        self.bouton_modifier_colonnes.pack(side="left", padx=10)

        # Treeview
        self.tree = ttk.Treeview(self, columns=(
            "nom", "code_fournisseur", "stock_actuel", "stock_alerte", "stock_maxi",
            "quantite_a_commander", "attente_livraison", "date_livraison_prevue",
            "en_rupture", "remplace_par"
        ), show="headings")
        self.tree.heading("nom", text="Nom", command=lambda: self.trier_colonne("nom"))
        self.tree.heading("code_fournisseur", text="Code Fournisseur", command=lambda: self.trier_colonne("code_fournisseur"))
        self.tree.heading("stock_actuel", text="Stock Actuel", command=lambda: self.trier_colonne("stock_actuel"))
        self.tree.heading("stock_alerte", text="Stock Alerte", command=lambda: self.trier_colonne("stock_alerte"))
        self.tree.heading("stock_maxi", text="Stock Maxi", command=lambda: self.trier_colonne("stock_maxi"))
        self.tree.heading("quantite_a_commander", text="À Commander", command=lambda: self.trier_colonne("quantite_a_commander"))
        self.tree.heading("attente_livraison", text="En Attente", command=lambda: self.trier_colonne("attente_livraison"))
        self.tree.heading("date_livraison_prevue", text="Livraison Prévue", command=lambda: self.trier_colonne("date_livraison_prevue"))
        self.tree.heading("en_rupture", text="Rupture ?", command=lambda: self.trier_colonne("en_rupture"))
        self.tree.heading("remplace_par", text="Remplacé par", command=lambda: self.trier_colonne("remplace_par"))
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

        # Bouton fictif pour test
        bouton = tk.Button(self, text="🔄 Rafraîchir Stock", command=self.rafraichir_stock)
        bouton.pack(pady=10)

    def ouvrir_fenetre_colonnes_personnalisees(self):
        from interfaces.colonnes_personnalisees_stock import ColonnesStockWindow
        ColonnesStockWindow(self, self.appliquer_colonnes_personnalisees)

    def appliquer_colonnes_personnalisees(self, colonnes_selectionnees):
        self.colonnes_personnalisees = colonnes_selectionnees
        self.mode_affichage.set("personnalise")
        self.rafraichir_stock()
        self.bouton_modifier_colonnes.config(state="normal")
        if not hasattr(self, "_apercu_deja_affiche") or not self._apercu_deja_affiche:
            self.afficher_apercu_colonnes_personnalisees()
            self._apercu_deja_affiche = True

    def afficher_apercu_colonnes_personnalisees(self):
        if hasattr(self, "fenetre_apercu") and self.fenetre_apercu.winfo_exists():
            self.fenetre_apercu.destroy()

        self.fenetre_apercu = tk.Toplevel(self)
        self.fenetre_apercu.title("Colonnes affichées (vue personnalisée)")
        self.fenetre_apercu.geometry("250x400+1200+200")
        self.fenetre_apercu.attributes("-topmost", True)

        label = tk.Label(self.fenetre_apercu, text="Colonnes activées :", font=("Helvetica", 10, "bold"))
        label.pack(pady=(10, 5))

        # Liste complète des colonnes disponibles (comme dans "complet")
        colonnes_possibles = [
            "nom", "code_fournisseur", "code_gtin", "code_cip", "stock_initial",
            "stock_actuel", "stock_alerte", "stock_maxi", "quantite_a_commander",
            "attente_livraison", "date_livraison_prevue", "commande_en_attente",
            "date_derniere_commande", "fournisseur_principal", "quantite_commandee",
            "quantite_livree", "quantite_retournee", "prix_unitaire", "en_rupture",
            "date_rupture", "date_fin_rupture", "rupture_definitive", "remplace_par"
        ]

        self.check_vars = {}
        for col in colonnes_possibles:
            var = tk.BooleanVar(value=col in self.colonnes_personnalisees)
            cb = tk.Checkbutton(self.fenetre_apercu, text=col, variable=var,
                                command=self.mettre_a_jour_colonnes_personnalisees)
            cb.pack(anchor="w", padx=10)
            self.check_vars[col] = var

        bouton_editeur = tk.Button(self.fenetre_apercu, text="🧩 Modifier via éditeur complet", command=self.ouvrir_fenetre_colonnes_personnalisees)
        bouton_editeur.pack(pady=(10, 5))

        bouton_fermer = tk.Button(self.fenetre_apercu, text="Fermer", command=self.fenetre_apercu.destroy)
        bouton_fermer.pack(pady=(5, 10))

    def mettre_a_jour_colonnes_personnalisees(self):
        self.colonnes_personnalisees = [col for col, var in self.check_vars.items() if var.get()]
        self.rafraichir_stock()

    def rafraichir_stock(self):
        import sqlite3

        # Connexion base
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        mode = self.mode_affichage.get()
        if mode == "minimal":
            colonnes = ("nom", "stock_actuel", "stock_alerte")
        elif mode == "standard":
            colonnes = (
                "nom", "code_fournisseur", "stock_actuel", "stock_alerte", "stock_maxi",
                "quantite_a_commander", "attente_livraison", "date_livraison_prevue",
                "en_rupture", "remplace_par"
            )
        elif mode == "complet":
            colonnes = (
                "nom", "code_fournisseur", "code_gtin", "code_cip", "stock_initial",
                "stock_actuel", "stock_alerte", "stock_maxi", "quantite_a_commander",
                "attente_livraison", "date_livraison_prevue", "commande_en_attente",
                "date_derniere_commande", "fournisseur_principal", "quantite_commandee",
                "quantite_livree", "quantite_retournee", "prix_unitaire", "en_rupture",
                "date_rupture", "date_fin_rupture", "rupture_definitive", "remplace_par"
            )
        elif mode == "personnalise" and hasattr(self, "colonnes_personnalisees"):
            colonnes = tuple(self.colonnes_personnalisees)
        else:
            colonnes = ("nom", "stock_actuel")  # fallback

        champs = ", ".join(colonnes)
        cur.execute(f"SELECT {champs} FROM medicaments")
        resultats = cur.fetchall()

        # Vider Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insérer les données
        for ligne in resultats:
            self.tree.insert("", "end", values=ligne)

        filtres_actifs = []
        if self.filtre_nom.get():
            filtres_actifs.append(f'Nom contient "{self.filtre_nom.get()}"')
        if self.filtre_fournisseur.get():
            filtres_actifs.append(f'Fournisseur contient "{self.filtre_fournisseur.get()}"')
        if self.filtre_rupture.get():
            filtres_actifs.append(f'Rupture = {self.filtre_rupture.get()}')
        self.label_filtres.config(text=" | ".join(filtres_actifs) if filtres_actifs else "")

        conn.close()

    def trier_colonne(self, col, reverse=False):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children()]
        try:
            l.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=reverse)
        except ValueError:
            l.sort(key=lambda t: t[0].lower() if t[0] else "", reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.trier_colonne(col, not reverse))

    def recherche_rapide(self):
        champ = self.champ_recherche.get()
        valeur = self.valeur_recherche.get().lower()

        for row in self.tree.get_children():
            self.tree.delete(row)

        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        colonnes = (
            "nom", "code_fournisseur", "stock_actuel", "stock_alerte", "stock_maxi",
            "quantite_a_commander", "attente_livraison", "date_livraison_prevue",
            "en_rupture", "remplace_par"
        )
        champs_sql = ", ".join(colonnes)
        cur.execute(f"SELECT {champs_sql} FROM medicaments")
        resultats = cur.fetchall()
        conn.close()

        for ligne in resultats:
            d = dict(zip(colonnes, ligne))
            if champ in d and valeur in str(d[champ]).lower():
                self.tree.insert("", "end", values=ligne)
    def ouvrir_recherche_multicritere(self):
        from interfaces.search_stock import SearchStockWindow
        SearchStockWindow(self, self.appliquer_filtres_stock)

    def appliquer_filtres_stock(self, filtres):
        champ_sql = (
            "nom", "code_fournisseur", "stock_actuel", "stock_alerte", "stock_maxi",
            "quantite_a_commander", "attente_livraison", "date_livraison_prevue",
            "en_rupture", "remplace_par"
        )

        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"SELECT {', '.join(champ_sql)} FROM medicaments")
        resultats = cur.fetchall()
        conn.close()

        # Vider table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Appliquer les filtres
        for ligne in resultats:
            d = dict(zip(champ_sql, ligne))
            if filtres["nom"] and filtres["nom"].lower() not in d["nom"].lower():
                continue
            if filtres["code_fournisseur"] and filtres["code_fournisseur"].lower() not in d["code_fournisseur"].lower():
                continue
            if filtres["en_rupture"] and str(d["en_rupture"]) != str(filtres["en_rupture"]):
                continue
            self.tree.insert("", "end", values=ligne)
    def reinitialiser_filtres(self):
        self.valeur_recherche.set("")
        # Si ces attributs existent (multicritère), on les réinitialise sinon on les ignore
        if hasattr(self, "filtre_nom"):
            self.filtre_nom.set("")
        if hasattr(self, "filtre_fournisseur"):
            self.filtre_fournisseur.set("")
        if hasattr(self, "filtre_rupture"):
            self.filtre_rupture.set("")
        self.rafraichir_stock()

    def exporter_vue_csv(self):
        import csv
        from tkinter import filedialog, messagebox

        colonnes = [self.tree.heading(c)["text"] for c in self.tree["columns"]]
        donnees = [self.tree.item(i)["values"] for i in self.tree.get_children()]

        if not donnees:
            messagebox.showinfo("Export CSV", "Aucune donnée à exporter.")
            return

        fichier = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if fichier:
            try:
                with open(fichier, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(colonnes)
                    writer.writerows(donnees)
                messagebox.showinfo("Export CSV", f"Export réussi : {fichier}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export : {e}")