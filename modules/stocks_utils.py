

"""
Fonctions utilitaires pour la gestion du stock de médicaments.
"""

def est_en_rupture(quantite_actuelle: int, quantite_min: int) -> bool:
    """
    Détermine si un médicament est en rupture de stock.

    :param quantite_actuelle: Quantité actuelle en stock
    :param quantite_min: Seuil minimal à maintenir
    :return: True si en dessous du seuil, False sinon
    """
    return quantite_actuelle < quantite_min