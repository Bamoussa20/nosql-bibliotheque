"""
indexes.py
----------
Crée et vérifie les index de la collection "books".

Deux index sont définis :

1. Un index simple sur "titre" : accélère la recherche par titre
   (recherche exacte et recherche par préfixe) et évite un scan
   complet de la collection (COLLSCAN) à chaque recherche de livre.

2. Un index composé { "disponible": 1, "date_publication": -1 } :
   pensé pour la requête la plus fréquente de l'application, celle de
   la page d'accueil qui affiche les livres disponibles triés du plus
   récent au plus ancien. MongoDB peut alors utiliser directement
   l'index pour filtrer ET trier, sans étape de tri en mémoire
   (SORT_KEY_GENERATOR / in-memory sort) supplémentaire.
"""

import config


def create_all_indexes(db) -> None:
    """Crée l'ensemble des index nécessaires au bon fonctionnement du projet."""
    books = db[config.COLLECTION_BOOKS]

    # Index simple sur le titre, utilisé par search_books_by_title()
    # et get_book_by_id() de façon indirecte (recherches par titre).
    title_index_name = books.create_index("titre", name="idx_titre")

    # Index composé pour la requête "livres disponibles triés par date
    # de publication décroissante", typiquement utilisée pour la page
    # d'accueil de la bibliothèque numérique.
    compound_index_name = books.create_index(
        [("disponible", 1), ("date_publication", -1)],
        name="idx_disponible_date_publication",
    )

    print(f"Index créé : {title_index_name}")
    print(f"Index composé créé : {compound_index_name}")


def list_indexes(db) -> list:
    """Retourne la liste des index existants sur la collection 'books'."""
    return list(db[config.COLLECTION_BOOKS].list_indexes())


def explain_title_search(db, keyword: str) -> dict:
    """
    Exécute explain() sur une recherche par titre afin de vérifier que
    l'index "idx_titre" est bien utilisé par le planificateur de requêtes.

    Utile pour démontrer, dans le rapport, le passage d'un COLLSCAN
    (parcours complet) à un IXSCAN (parcours d'index) grâce à l'index.
    """
    query = {"titre": {"$regex": f"^{keyword}", "$options": "i"}}
    return db[config.COLLECTION_BOOKS].find(query).explain()


def explain_available_books_sorted(db) -> dict:
    """
    Exécute explain() sur la requête "livres disponibles triés par date
    de publication décroissante", afin de vérifier l'utilisation de
    l'index composé "idx_disponible_date_publication".
    """
    cursor = (
        db[config.COLLECTION_BOOKS]
        .find({"disponible": True})
        .sort("date_publication", -1)
    )
    return cursor.explain()
