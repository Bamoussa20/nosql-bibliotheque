"""
crud.py
-------
Implémente les opérations CRUD (Create, Read, Update, Delete) de base
sur la collection "books" de la bibliothèque numérique.

Chaque fonction est indépendante et réutilisable, aussi bien depuis
main.py que depuis un script de test.
"""

from bson import ObjectId
from bson.errors import InvalidId

import config


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def create_book(db, book_data: dict):
    """
    Insère un nouveau livre dans la collection "books".

    Args:
        db: base de données MongoDB.
        book_data (dict): document du livre à insérer.

    Returns:
        ObjectId: identifiant du document inséré, ou None en cas d'erreur.
    """
    try:
        result = db[config.COLLECTION_BOOKS].insert_one(book_data)
        return result.inserted_id
    except Exception as error:
        print(f"Erreur lors de l'insertion du livre : {error}")
        return None


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_all_books(db) -> list:
    """Retourne la liste de tous les livres de la bibliothèque."""
    return list(db[config.COLLECTION_BOOKS].find())


def get_book_by_id(db, book_id: str) -> dict:
    """
    Retourne un livre à partir de son identifiant.

    Args:
        book_id (str): identifiant du livre sous forme de chaîne.

    Returns:
        dict | None: le document trouvé, ou None si l'id est invalide
        ou si aucun livre ne correspond.
    """
    try:
        object_id = ObjectId(book_id)
    except InvalidId:
        print(f"Identifiant invalide : {book_id}")
        return None

    return db[config.COLLECTION_BOOKS].find_one({"_id": object_id})


def get_available_books(db) -> list:
    """Retourne uniquement les livres actuellement disponibles."""
    return list(db[config.COLLECTION_BOOKS].find({"disponible": True}))


def search_books_by_title(db, keyword: str) -> list:
    """
    Recherche les livres dont le titre contient le mot-clé donné
    (recherche insensible à la casse via une expression régulière).
    """
    regex_query = {"titre": {"$regex": keyword, "$options": "i"}}
    return list(db[config.COLLECTION_BOOKS].find(regex_query))


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def update_book_availability(db, book_id: str, disponible: bool) -> bool:
    """
    Met à jour le champ "disponible" d'un livre.

    Args:
        book_id (str): identifiant du livre.
        disponible (bool): nouvel état de disponibilité.

    Returns:
        bool: True si un document a été modifié, False sinon.
    """
    try:
        object_id = ObjectId(book_id)
    except InvalidId:
        print(f"Identifiant invalide : {book_id}")
        return False

    result = db[config.COLLECTION_BOOKS].update_one(
        {"_id": object_id},
        {"$set": {"disponible": disponible}},
    )
    return result.modified_count > 0


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def delete_book(db, book_id: str) -> bool:
    """
    Supprime un livre à partir de son identifiant.
    Prévu pour supprimer un document de test, jamais les données
    principales du jeu de données initial.

    Returns:
        bool: True si un document a été supprimé, False sinon.
    """
    try:
        object_id = ObjectId(book_id)
    except InvalidId:
        print(f"Identifiant invalide : {book_id}")
        return False

    result = db[config.COLLECTION_BOOKS].delete_one({"_id": object_id})
    return result.deleted_count > 0
