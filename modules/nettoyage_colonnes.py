def normaliser_colonnes_entetes(cols: list[str]) -> list[str]:
    """
    Transforme une liste d'entêtes pour qu'elles soient minuscules et sans espaces,
    par ex. ["Code CIP", " Nom "] → ["code_cip", "nom"].
    """
    return [c.strip().lower().replace(" ", "_") for c in cols]