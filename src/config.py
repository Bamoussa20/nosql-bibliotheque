"""
config.py
---------
Charge la configuration de l'application depuis les variables d'environnement.

Ce module ne contient aucun identifiant en dur : l'URI de connexion à
MongoDB Atlas est lue depuis un fichier .env (non versionné) grâce à
python-dotenv.
"""

import os
from dotenv import load_dotenv

# Charge le fichier .env s'il existe (utile en développement local)
load_dotenv()

# URI de connexion MongoDB (Atlas ou instance locale/Docker)
MONGODB_URI = os.getenv("MONGODB_URI")

# Nom de la base de données utilisée par le projet
DATABASE_NAME = os.getenv("DATABASE_NAME", "bibliotheque_nosql")

# Noms des collections (centralisés pour éviter les fautes de frappe
# et les incohérences entre les différents modules)
COLLECTION_BOOKS = "books"
COLLECTION_AUTHORS = "authors"
COLLECTION_LOANS = "loans"
COLLECTION_USERS = "users"


def validate_config() -> None:
    """
    Vérifie que la configuration minimale est présente avant de
    tenter une connexion à la base de données.

    Lève une exception explicite si MONGODB_URI est absent, plutôt que
    de laisser PyMongo échouer avec une erreur peu compréhensible.
    """
    if not MONGODB_URI:
        raise EnvironmentError(
            "La variable d'environnement MONGODB_URI est manquante. "
            "Copiez .env.example vers .env et renseignez votre URI "
            "MongoDB Atlas avant de lancer le projet."
        )
