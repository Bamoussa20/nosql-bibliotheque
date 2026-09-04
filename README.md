# Bibliothèque Numérique — Projet NoSQL / MongoDB

## Présentation

Ce projet est réalisé dans le cadre du devoir **« Exploration et Implémentation NoSQL »**.
Il consiste à concevoir et implémenter une base de données documentaire
MongoDB pour la gestion d'une bibliothèque numérique : livres, auteurs,
utilisateurs et emprunts.

Le projet démontre, sur un cas concret, les principes de modélisation
NoSQL (embedding vs referencing, conception orientée requêtes), ainsi
que la mise en œuvre de requêtes CRUD, de pipelines d'agrégation et
d'index avec **PyMongo**.

## Objectifs pédagogiques

- Comprendre les compromis entre bases relationnelles et bases NoSQL.
- Modéliser une base documentaire en fonction des besoins applicatifs.
- Mettre en pratique le CRUD, les pipelines d'agrégation et
  l'indexation avec MongoDB et PyMongo.
- Manipuler MongoDB Atlas dans un contexte proche d'un usage
  professionnel réel.

## Technologies utilisées

- **Python 3.10+**
- **MongoDB** (via **MongoDB Atlas**, cluster gratuit M0)
- **PyMongo** pour l'accès à la base depuis Python
- **python-dotenv** pour la gestion de la configuration
- **Git / GitHub** pour le versionnement du code

## Architecture du projet

```text
nosql-bibliotheque/
│
├── README.md                # Ce fichier
├── requirements.txt         # Dépendances Python
├── .env.example              # Modèle de configuration (sans identifiants réels)
├── .gitignore
│
├── src/
│   ├── config.py             # Lecture de la configuration (.env)
│   ├── database.py           # Connexion à MongoDB
│   ├── init_database.py      # Initialisation et peuplement de la base
│   ├── crud.py                # Opérations Create / Read / Update / Delete
│   ├── aggregations.py       # Pipelines d'agrégation
│   ├── indexes.py             # Création et vérification des index
│   └── main.py                 # Démonstration complète des fonctionnalités
│
├── data/
│   └── sample_data.json      # Aperçu lisible du jeu de données inséré
│
├── docs/
│   └── schema.json            # Schéma documenté des collections
│
├── tests/
│   └── test_project.py       # Vérifications de bon fonctionnement
│
└── rapport/
    └── rapport.md             # Rapport académique complet
```

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-depot>
cd nosql-bibliotheque
```

### 2. Créer un environnement virtuel

**Linux / macOS :**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows :**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Configuration de MongoDB Atlas

1. **Créer un compte** sur [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) si nécessaire.
2. **Créer un cluster** : choisir l'offre gratuite **M0**, une région
   proche, puis valider la création (quelques minutes).
3. **Créer un utilisateur de base de données** : dans *Database
   Access*, créer un utilisateur avec un nom d'utilisateur et un mot
   de passe (à conserver en lieu sûr, ils seront utilisés dans l'URI
   de connexion).
4. **Autoriser votre adresse IP** : dans *Network Access*, ajouter
   votre adresse IP actuelle, ou `0.0.0.0/0` pour un accès depuis
   n'importe quelle IP (à réserver à un usage de développement/démo).
5. **Récupérer l'URI de connexion** : dans *Database* → *Connect* →
   *Drivers*, sélectionner Python et copier l'URI proposée, de la
   forme :

   ```text
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
   ```

6. **Créer le fichier `.env`** à la racine du projet, à partir du
   modèle fourni :

   ```bash
   cp .env.example .env
   ```

   Puis éditer `.env` et renseigner votre URI :

   ```text
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
   ```

   > Le fichier `.env` ne doit **jamais** être versionné sur GitHub.
   > Il est déjà exclu via `.gitignore`.

### Alternative : MongoDB via Docker

Si vous préférez une instance locale plutôt qu'Atlas :

```bash
docker run -d --name mongo-bibliotheque -p 27017:27017 mongo:7
```

Puis, dans `.env` :

```text
MONGODB_URI=mongodb://localhost:27017/
```

## Exécution du projet

### 1. Initialiser la base de données

Vide les collections, insère le jeu de données de démonstration et
crée les index :

```bash
python src/init_database.py
```

### 2. Lancer la démonstration complète

Exécute les opérations CRUD, les agrégations et la vérification des
index :

```bash
python src/main.py
```

### 3. Exécuter les tests

```bash
python tests/test_project.py
```

ou, si `pytest` est installé :

```bash
python -m pytest tests/ -v
```

## Fonctionnalités implémentées

- Connexion sécurisée à MongoDB Atlas via variable d'environnement.
- Insertion d'un jeu de données réaliste (auteurs, utilisateurs,
  livres aux structures variées, emprunts).
- **CRUD** complet sur la collection `books` :
  - création d'un livre ;
  - lecture de tous les livres, par id, par disponibilité, par titre ;
  - mise à jour de la disponibilité ;
  - suppression d'un document de test.
- **Agrégations** :
  - nombre de livres par auteur ;
  - livres actuellement empruntés et non rendus.
- **Index** :
  - index simple sur `titre` ;
  - index composé sur `{ disponible, date_publication }`.
- Suite de tests de vérification du bon fonctionnement de bout en bout.

## Agrégations — résultats attendus

**Nombre de livres par auteur** (avec le jeu de données fourni) :

| Auteur              | Nombre de livres |
|----------------------|-------------------|
| George Orwell        | 2                 |
| Robert C. Martin     | 2                 |
| Isaac Asimov          | 1                 |
| Yuval Noah Harari    | 1                 |

**Livres empruntés non rendus** : la requête retourne les emprunts dont
le champ `date_retour` est `null`, avec le titre du livre concerné,
le nom de l'emprunteur et un indicateur de retard calculé par rapport
à la date du jour.

## Index

- `idx_titre` : accélère les recherches et tris par titre (utilisé par
  `search_books_by_title`), en évitant un parcours complet de la
  collection (`COLLSCAN`).
- `idx_disponible_date_publication` : index composé pensé pour la
  requête « livres disponibles, triés par date de publication
  décroissante », typique d'une page d'accueil. Il permet à MongoDB de
  filtrer **et** trier directement via l'index, sans tri en mémoire
  supplémentaire.


