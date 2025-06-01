import sqlite3
from pathlib import Path
import hashlib

# Chemin vers la base (sera créée si elle n'existe pas)
DB_PATH = Path("db/base_stock.sqlite")

def ensure_schema():
    # Crée le dossier db s’il n’existe pas
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1) Table fournisseurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fournisseurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL
        )
    """)

    # 2) Table médicaments (produit unique)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            dci TEXT,
            classe_therapeutique TEXT,
            activite TEXT,
            fabricant TEXT,
            poids TEXT,
            unites_de_vente TEXT,
            tva REAL
        )
    """)

    # 3) Table références_fournisseurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS references_fournisseurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_medicament INTEGER NOT NULL,
            fournisseur_id INTEGER NOT NULL,
            code_gtin TEXT,
            code_cip TEXT,
            code_fournisseur TEXT,
            par_lot_de INTEGER,
            tarif_unitaire REAL,
            tarif_unitaire_par_lot REAL,
            date_import DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_medicament) REFERENCES medicaments(id),
            FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id)
        )
    """)

    # 4) Table journal d’audit
    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horodatage DATETIME DEFAULT CURRENT_TIMESTAMP,
            action TEXT,
            message TEXT,
            utilisateur TEXT
        )
    """)
                
    # 5) Table utilisateurs (pour gérer l’authentification)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL
        )
    """)

    # 6) Insère un compte admin par défaut si introuvable (à supprimer , utilisé uniquement pour le développement et les tests)
    #     Mot de passe “admin123” haché en SHA-256
    admin_hash = hashlib.sha256("admin123".encode("utf-8")).hexdigest()
    # On utilise INSERT OR IGNORE pour ne pas dupliquer si déjà présent
    cur.execute("""
        INSERT OR IGNORE INTO utilisateurs (nom, mot_de_passe)
        VALUES ('admin', ?)
    """, (admin_hash,))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    ensure_schema()
    print("Base initialisée ; modèle “par médicament”.")