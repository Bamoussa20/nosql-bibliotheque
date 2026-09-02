"""
aggregations.py
----------------
Contient les pipelines d'agrégation MongoDB demandées par le devoir :

1. Nombre de livres par auteur.
2. Livres actuellement empruntés et non rendus, avec les informations
   du livre et de l'utilisateur concerné.
"""

from datetime import datetime

import config


def books_count_by_author(db) -> list:
    """
    Calcule le nombre de livres écrits par chaque auteur.

    Pipeline :
        1. $unwind sur "auteurs" : chaque livre ayant plusieurs auteurs
           est éclaté en plusieurs documents temporaires, un par auteur,
           afin de pouvoir compter individuellement la contribution de
           chaque auteur.
        2. $group sur "auteurs.auteur_id" : regroupe les documents par
           auteur et compte le nombre de livres associés avec $sum.
        3. $lookup sur la collection "authors" : récupère le nom complet
           et les informations de l'auteur à partir de son _id.
        4. $unwind sur le résultat du $lookup : la jointure retourne un
           tableau ; comme on attend un seul auteur par _id, on l'aplatit.
        5. $project : ne garde que les champs utiles pour l'affichage
           final (nom de l'auteur, nombre de livres).
        6. $sort : trie les auteurs par nombre de livres décroissant.
    """
    pipeline = [
        {"$unwind": "$auteurs"},
        {
            "$group": {
                "_id": "$auteurs.auteur_id",
                "nombre_livres": {"$sum": 1},
            }
        },
        {
            "$lookup": {
                "from": config.COLLECTION_AUTHORS,
                "localField": "_id",
                "foreignField": "_id",
                "as": "auteur_info",
            }
        },
        {"$unwind": "$auteur_info"},
        {
            "$project": {
                "_id": 0,
                "auteur": "$auteur_info.nom",
                "nombre_livres": 1,
            }
        },
        {"$sort": {"nombre_livres": -1}},
    ]

    return list(db[config.COLLECTION_BOOKS].aggregate(pipeline))


def books_currently_borrowed(db) -> list:
    """
    Retourne les livres actuellement empruntés et non rendus à ce jour.

    Un emprunt est considéré comme "non rendu" lorsque son champ
    "date_retour" vaut None (aucune date de retour enregistrée), quel
    que soit le statut textuel stocké par ailleurs. C'est ce critère,
    factuel et non ambigu, qui est utilisé comme filtre principal.

    Pipeline :
        1. $match sur "date_retour" = null : ne conserve que les
           emprunts non clôturés.
        2. $lookup sur "books" : associe chaque emprunt à son livre.
        3. $lookup sur "users" : associe chaque emprunt à son utilisateur.
        4. $unwind sur les deux jointures (un seul livre / utilisateur
           par emprunt).
        5. $project : construit un document de sortie lisible avec le
           titre du livre, le nom de l'emprunteur, les dates clés et
           un indicateur de retard calculé côté application.
        6. $sort : les emprunts les plus anciens en premier (les plus
           susceptibles d'être en retard).
    """
    pipeline = [
        {"$match": {"date_retour": None}},
        {
            "$lookup": {
                "from": config.COLLECTION_BOOKS,
                "localField": "livre_id",
                "foreignField": "_id",
                "as": "livre",
            }
        },
        {"$unwind": "$livre"},
        {
            "$lookup": {
                "from": config.COLLECTION_USERS,
                "localField": "utilisateur_id",
                "foreignField": "_id",
                "as": "utilisateur",
            }
        },
        {"$unwind": "$utilisateur"},
        {
            "$project": {
                "_id": 0,
                "titre_livre": "$livre.titre",
                "emprunteur": "$utilisateur.nom",
                "date_emprunt": 1,
                "date_retour_prevue": 1,
            }
        },
        {"$sort": {"date_emprunt": 1}},
    ]

    results = list(db[config.COLLECTION_LOANS].aggregate(pipeline))

    # Le retard est calculé côté application par rapport à la date du jour,
    # car il dépend du moment de l'exécution et ne doit pas être stocké
    # de façon dénormalisée dans le pipeline lui-même.
    today = datetime.utcnow()
    for loan in results:
        loan["en_retard"] = loan["date_retour_prevue"] < today

    return results
