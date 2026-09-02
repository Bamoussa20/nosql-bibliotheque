"""
init_database.py
-----------------
Initialise la base de données de la bibliothèque numérique :
- vide les collections existantes (pour permettre une exécution répétée) ;
- insère des auteurs, des utilisateurs, des livres et des emprunts
  cohérents entre eux ;
- crée les index définis dans indexes.py.

Ce script est fait pour être exécuté une seule fois au démarrage du
projet, ou à chaque fois que l'on souhaite repartir d'un jeu de
données propre.
"""

from datetime import datetime, timedelta

import config
from database import get_database, close_connection
from indexes import create_all_indexes


def reset_collections(db) -> None:
    """Supprime le contenu des collections pour repartir d'une base vide."""
    db[config.COLLECTION_BOOKS].delete_many({})
    db[config.COLLECTION_AUTHORS].delete_many({})
    db[config.COLLECTION_LOANS].delete_many({})
    db[config.COLLECTION_USERS].delete_many({})
    print("Collections vidées.")


def insert_authors(db) -> dict:
    """
    Insère les auteurs et retourne un dictionnaire {nom: _id} afin de
    pouvoir référencer facilement ces auteurs depuis les livres.
    """
    authors = [
        {
            "nom": "George Orwell",
            "bio": "Écrivain et journaliste britannique, connu pour ses "
                   "œuvres dystopiques et son engagement politique.",
            "nationalite": "Britannique",
        },
        {
            "nom": "Robert C. Martin",
            "bio": "Ingénieur logiciel américain, auteur de référence sur "
                   "les bonnes pratiques de développement.",
            "nationalite": "Américaine",
        },
        {
            "nom": "Isaac Asimov",
            "bio": "Écrivain et biochimiste américain, figure majeure de "
                   "la science-fiction du XXe siècle.",
            "nationalite": "Américaine",
        },
        {
            "nom": "Yuval Noah Harari",
            "bio": "Historien et essayiste israélien, spécialiste de "
                   "l'histoire mondiale et de la prospective.",
            "nationalite": "Israélienne",
        },
    ]

    result = db[config.COLLECTION_AUTHORS].insert_many(authors)
    ids_by_name = {
        author["nom"]: _id for author, _id in zip(authors, result.inserted_ids)
    }
    print(f"{len(result.inserted_ids)} auteurs insérés.")
    return ids_by_name


def insert_users(db) -> dict:
    """Insère les utilisateurs de la bibliothèque et retourne leurs ids par nom."""
    users = [
        {"nom": "Amadou Diallo", "email": "amadou.diallo@example.com"},
        {"nom": "Fatoumata Camara", "email": "fatoumata.camara@example.com"},
        {"nom": "Mamadou Bah", "email": "mamadou.bah@example.com"},
    ]

    result = db[config.COLLECTION_USERS].insert_many(users)
    ids_by_name = {
        user["nom"]: _id for user, _id in zip(users, result.inserted_ids)
    }
    print(f"{len(result.inserted_ids)} utilisateurs insérés.")
    return ids_by_name


def build_author_ref(author_id, nom: str) -> dict:
    """
    Construit la référence "étendue" d'un auteur telle qu'elle est
    embarquée dans un document livre : l'_id (pour la relation) et le
    nom (pour l'affichage direct sans jointure supplémentaire).
    """
    return {"auteur_id": author_id, "nom": nom}


def insert_books(db, author_ids: dict) -> dict:
    """
    Insère 5 livres aux structures volontairement différentes, afin de
    montrer la flexibilité du modèle documentaire de MongoDB.

    Retourne un dictionnaire {titre: _id} pour permettre de créer des
    emprunts cohérents ensuite.
    """
    books = [
        {
            # Livre avec un seul auteur, plusieurs tags, résumé complet, disponible
            "titre": "1984",
            "auteurs": [build_author_ref(author_ids["George Orwell"], "George Orwell")],
            "date_publication": datetime(1949, 6, 8),
            "tags": ["Dystopie", "Science-fiction", "Politique"],
            "resume": (
                "Dans un monde totalitaire sous surveillance permanente, "
                "Winston Smith tente de préserver sa liberté de pensée "
                "face au régime de Big Brother."
            ),
            "disponible": True,
        },
        {
            # Livre avec un seul auteur, un seul tag, résumé court, indisponible
            "titre": "Clean Code",
            "auteurs": [build_author_ref(author_ids["Robert C. Martin"], "Robert C. Martin")],
            "date_publication": datetime(2008, 8, 1),
            "tags": ["Génie logiciel"],
            "resume": "Un guide de référence sur l'écriture d'un code lisible et maintenable.",
            "disponible": False,
        },
        {
            # Livre avec plusieurs tags, sans mention explicite du genre dans le résumé
            "titre": "Fondation",
            "auteurs": [build_author_ref(author_ids["Isaac Asimov"], "Isaac Asimov")],
            "date_publication": datetime(1951, 5, 1),
            "tags": ["Science-fiction", "Space opera", "Roman"],
            "resume": (
                "L'effondrement annoncé d'un empire galactique donne "
                "naissance à un projet scientifique destiné à réduire "
                "des millénaires de chaos à un seul siècle."
            ),
            "disponible": True,
        },
        {
            # Livre sans tag, résumé plus long, plusieurs auteurs simulés
            # (Harari cité seul ici, mais structure prête pour plusieurs auteurs)
            "titre": "Sapiens : Une brève histoire de l'humanité",
            "auteurs": [build_author_ref(author_ids["Yuval Noah Harari"], "Yuval Noah Harari")],
            "date_publication": datetime(2011, 1, 1),
            "tags": [],
            "resume": (
                "Une traversée de l'histoire humaine, de l'apparition de "
                "l'Homo sapiens à la révolution cognitive, agricole puis "
                "scientifique, interrogeant les mythes fondateurs de nos "
                "sociétés et leurs conséquences sur le monde actuel."
            ),
            "disponible": True,
        },
        {
            # Livre avec deux auteurs et disponibilité fausse, pour varier la structure
            "titre": "Le Guide du développeur pragmatique",
            "auteurs": [
                build_author_ref(author_ids["Robert C. Martin"], "Robert C. Martin"),
                build_author_ref(author_ids["George Orwell"], "George Orwell"),
            ],
            "date_publication": datetime(2019, 3, 15),
            "tags": ["Génie logiciel", "Méthodologie"],
            "resume": "Compilation de bonnes pratiques transversales pour le développement logiciel.",
            "disponible": False,
        },
    ]

    result = db[config.COLLECTION_BOOKS].insert_many(books)
    ids_by_title = {
        book["titre"]: _id for book, _id in zip(books, result.inserted_ids)
    }
    print(f"{len(result.inserted_ids)} livres insérés.")
    return ids_by_title


def insert_loans(db, book_ids: dict, user_ids: dict) -> None:
    """
    Insère des emprunts référençant les livres et les utilisateurs par
    leur ObjectId. Certains emprunts sont rendus, d'autres non, afin de
    pouvoir démontrer l'agrégation des emprunts en cours.
    """
    now = datetime.utcnow()

    loans = [
        {
            "utilisateur_id": user_ids["Amadou Diallo"],
            "livre_id": book_ids["1984"],
            "date_emprunt": now - timedelta(days=10),
            "date_retour_prevue": now - timedelta(days=0),
            "date_retour": None,
            "statut": "en_cours",
        },
        {
            "utilisateur_id": user_ids["Fatoumata Camara"],
            "livre_id": book_ids["Clean Code"],
            "date_emprunt": now - timedelta(days=20),
            "date_retour_prevue": now - timedelta(days=6),
            "date_retour": None,
            "statut": "en_cours",
        },
        {
            "utilisateur_id": user_ids["Mamadou Bah"],
            "livre_id": book_ids["Fondation"],
            "date_emprunt": now - timedelta(days=30),
            "date_retour_prevue": now - timedelta(days=16),
            "date_retour": now - timedelta(days=15),
            "statut": "rendu",
        },
        {
            "utilisateur_id": user_ids["Amadou Diallo"],
            "livre_id": book_ids["Le Guide du développeur pragmatique"],
            "date_emprunt": now - timedelta(days=5),
            "date_retour_prevue": now + timedelta(days=9),
            "date_retour": None,
            "statut": "en_cours",
        },
    ]

    result = db[config.COLLECTION_LOANS].insert_many(loans)
    print(f"{len(result.inserted_ids)} emprunts insérés.")


def main() -> None:
    db = get_database()
    print(f"Connexion établie à la base '{db.name}'.")

    reset_collections(db)

    author_ids = insert_authors(db)
    user_ids = insert_users(db)
    book_ids = insert_books(db, author_ids)
    insert_loans(db, book_ids, user_ids)

    create_all_indexes(db)

    print("Initialisation de la base terminée avec succès.")
    close_connection()


if __name__ == "__main__":
    main()
