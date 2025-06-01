import sqlite3

def ajouter_colonnes_si_absentes(nom_table: str, colonnes: dict, db_path: str):
    """
    Ajoute à la table les colonnes manquantes.

    :param nom_table: Nom de la table à modifier
    :param colonnes: Dictionnaire {nom_colonne: type_sql}
    :param db_path: Chemin vers la base SQLite
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Obtenir la liste des colonnes existantes
    cur.execute(f"PRAGMA table_info({nom_table})")
    colonnes_existantes = [ligne[1] for ligne in cur.fetchall()]

    # Ajouter les colonnes manquantes
    for colonne, type_sql in colonnes.items():
        if colonne not in colonnes_existantes:
            cur.execute(f"ALTER TABLE {nom_table} ADD COLUMN {colonne} {type_sql}")

    conn.commit()
    conn.close()


# Ajoute les colonnes liées à la gestion de stock complet pour la table "medicaments"
def ajouter_colonnes_stock_complet(db_path: str):
    colonnes_stock = {
        "code_fournisseur": "TEXT",
        "code_gtin": "TEXT",
        "code_cip": "TEXT",
        "stock_actuel": "INTEGER",
        "stock_alerte": "INTEGER",
        "stock_maxi": "INTEGER",
        "quantite_a_commander": "INTEGER",
        "stock_initial": "INTEGER",
        "attente_livraison": "INTEGER",
        "date_livraison_prevue": "TEXT",
        "commande_en_attente": "INTEGER",  # booléen 0/1
        "date_derniere_commande": "TEXT",
        "fournisseur_principal": "TEXT",
        "quantite_commandee": "INTEGER",
        "quantite_livree": "INTEGER",
        "quantite_retournee": "INTEGER",
        "prix_unitaire": "REAL",
        "en_rupture": "INTEGER",
        "date_rupture": "TEXT",
        "date_fin_rupture": "TEXT",
        "rupture_definitive": "INTEGER",
        "remplace_par": "TEXT"
    }
    ajouter_colonnes_si_absentes("medicaments", colonnes_stock, db_path)