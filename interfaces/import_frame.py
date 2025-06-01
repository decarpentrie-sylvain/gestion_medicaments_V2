import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
from pathlib import Path
import hashlib

from modules.import_utils import lire_fichier, normaliser_colonnes
from modules.gestion_audit import log_action

DB_PATH = Path("db/base_stock.sqlite")

class ImportFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # ───── Bloc Connexion ────────────────────────────────────
        # Label “Utilisateur”, Combobox, Entry mot de passe, Boutons
        frame_conn = ttk.Frame(self)
        frame_conn.pack(fill="x", pady=(5,10), padx=5)

        ttk.Label(frame_conn, text="Utilisateur :").grid(row=0, column=0, sticky="e")
        self.combo_user = ttk.Combobox(frame_conn, values=self.charger_utilisateurs(), state="readonly")
        self.combo_user.grid(row=0, column=1, padx=5)

        ttk.Label(frame_conn, text="Mot de passe :").grid(row=0, column=2, sticky="e")
        self.entry_mdp = ttk.Entry(frame_conn, show="*")
        self.entry_mdp.grid(row=0, column=3, padx=5)
        self.entry_mdp.bind("<Return>", lambda e: self.se_connecter())

        self.btn_login = ttk.Button(frame_conn, text="🔐 Se connecter", command=self.se_connecter)
        self.btn_login.grid(row=0, column=4, padx=(5,0))
        self.btn_logout = ttk.Button(frame_conn, text="🔓 Déconnexion", command=self.se_deconnecter, state="disabled")
        self.btn_logout.grid(row=0, column=5, padx=5)

        self.label_utilisateur = ttk.Label(frame_conn, text="🔒 Non connecté", foreground="darkred")
        self.label_utilisateur.grid(row=1, column=0, columnspan=6, pady=(5,0))

        self.utilisateur_actif = None

        # Pour développement : on pré-remplit “admin” + “admin123” pour auto-login
        if "admin" in self.charger_utilisateurs():
            self.combo_user.set("admin")
            self.entry_mdp.insert(0, "admin123")
            self.after(100, self.se_connecter)

        # Ligne de séparation ou espace
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=(0,10))

        # ───── Suite du reste de l’onglet Import ─────────────────
        self.fichier_label = ttk.Label(self, text="Aucun fichier sélectionné")
        self.fichier_label.pack(pady=5)

        self.btn_choisir = ttk.Button(self, text="📂 Choisir fichier", command=self.choisir_fichier, state="disabled")
        self.btn_choisir.pack(pady=5)

        self.btn_importer = ttk.Button(self, text="✅ Importer", command=self.importer_fichier, state="disabled")
        self.btn_importer.pack(pady=5)

        self.status = ttk.Label(self, text="", foreground="green")
        self.status.pack(pady=5)

        self.chemin = None
        self.df = None

    # ─── Méthodes liées aux utilisateurs ─────────────────────────
    def charger_utilisateurs(self):
        """
        Renvoie la liste des noms d'utilisateurs existants en base.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT nom FROM utilisateurs ORDER BY nom")
            noms = [row[0] for row in cur.fetchall()]
            conn.close()
            return noms
        except Exception as e:
            messagebox.showerror("Erreur chargement utilisateurs", str(e))
            return []

    def se_connecter(self):
        """
        Vérifie la saisie utilisateur + mot de passe (SHA-256) et active l'interface.
        """
        nom = self.combo_user.get().strip()
        mdp = self.entry_mdp.get().strip()
        if not nom or not mdp:
            messagebox.showwarning("Connexion", "Nom ou mot de passe manquant.")
            return

        # Hachage du mot de passe
        mdp_hash = hashlib.sha256(mdp.encode("utf-8")).hexdigest()

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id FROM utilisateurs WHERE nom = ? AND mot_de_passe = ?", (nom, mdp_hash))
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur BDD", str(e))
            return

        if row:
            # Authentification OK
            self.utilisateur_actif = nom
            self.label_utilisateur.config(text=f"🔓 Connecté en tant que : {nom}", foreground="darkgreen")
            self.combo_user.config(state="disabled")
            self.entry_mdp.config(state="disabled")
            self.btn_login.config(state="disabled")
            self.btn_logout.config(state="normal")

            # Désormais, on peut activer les boutons Choisir + Importer
            self.btn_choisir.config(state="normal")

            # Pour que l’interface principale sache quel user est connecté et active l’onglet “Admin” en conséquence.
            if hasattr(self, "on_login") and callable(self.on_login):
                self.on_login(self.utilisateur_actif)
            else:
            # si aucun attribut on_login n’a été assigné au widget, ou si ce qu’on y a mis n’est pas callable (phase de développement)
                print("Pas de callback on_login définie.")
        else:
            messagebox.showerror("Erreur", "Nom ou mot de passe invalide.")

    def se_deconnecter(self):
        """
        Déconnecte l'utilisateur courant et bloque de nouveau l'accès à l'import.
        """
        self.utilisateur_actif = None
        self.combo_user.config(state="readonly")
        self.combo_user.set("")
        self.entry_mdp.config(state="normal")
        self.entry_mdp.delete(0, tk.END)
        self.btn_login.config(state="normal")
        self.btn_logout.config(state="disabled")

        self.label_utilisateur.config(text="🔒 Non connecté", foreground="darkred")

        # Désactive à nouveau la sélection de fichier
        self.btn_choisir.config(state="disabled")
        self.btn_importer.config(state="disabled")

    # ─── Méthodes d’import de fichier ─────────────────────────────
    def choisir_fichier(self):
        chemin = filedialog.askopenfilename(
            filetypes=[("Fichiers CSV/Excel", "*.csv *.xlsx"), ("Tous fichiers", "*.*")],
            title="Sélectionner un fichier de tarifs"
        )
        if not chemin:
            return

        self.chemin = chemin
        self.fichier_label.config(text=chemin)
        self.btn_importer.config(state="normal")
        self.status.config(text="")

    def importer_fichier(self):
        if not self.utilisateur_actif:
            messagebox.showwarning("Connexion requise", "Veuillez vous connecter avant d'importer.")
            return

        try:
            # Lecture + nettoyage du DataFrame
            df_raw, ext = lire_fichier(self.chemin)
            df = normaliser_colonnes(df_raw)
            self.df = df

            # Journalisation
            log_action("import_csv", f"Import de {self.chemin}", utilisateur=self.utilisateur_actif)

            self.status.config(text=f"{len(df)} lignes traitées (logué).")
        except Exception as e:
            messagebox.showerror("Erreur Import", str(e))
            self.status.config(text="Échec de l’import.", foreground="red")