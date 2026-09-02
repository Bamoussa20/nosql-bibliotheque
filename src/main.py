"""
main.py
-------
Point d'entrée du projet. Exécute une démonstration complète des
fonctionnalités développées : CRUD, agrégations et vérification des
index.

Prérequis : avoir exécuté au préalable `python src/init_database.py`
pour peupler la base de données.
"""

from pprint import pprint

from database import get_database, close_connection
import crud
import aggregations
import indexes


def print_section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def demo_crud(db) -> None:
    print_section("CRUD - Lecture de tous les livres")
    for book in crud.get_all_books(db):
        print(f"- {book['titre']} (disponible: {book['disponible']})")

    print_section("CRUD - Livres disponibles uniquement")
    for book in crud.get_available_books(db):
        print(f"- {book['titre']}")

    print_section("CRUD - Recherche par titre ('guide')")
    for book in crud.search_books_by_title(db, "guide"):
        print(f"- {book['titre']}")

    print_section("CRUD - Mise à jour de la disponibilité d'un livre")
    target_book = db["books"].find_one({"titre": "1984"})
    book_id = str(target_book["_id"])

    print("Avant modification :")
    pprint(crud.get_book_by_id(db, book_id))

    crud.update_book_availability(db, book_id, disponible=False)

    print("\nAprès modification :")
    pprint(crud.get_book_by_id(db, book_id))

    # On remet la valeur d'origine pour ne pas fausser les données de démo.
    crud.update_book_availability(db, book_id, disponible=True)

    print_section("CRUD - Création puis suppression d'un livre de test")
    test_book_id = crud.create_book(
        db,
        {
            "titre": "Livre de test temporaire",
            "auteurs": [],
            "date_publication": None,
            "tags": ["Test"],
            "resume": "Document créé uniquement pour valider le CREATE/DELETE.",
            "disponible": True,
        },
    )
    print(f"Livre de test créé avec l'id : {test_book_id}")

    deleted = crud.delete_book(db, str(test_book_id))
    print(f"Suppression du livre de test réussie : {deleted}")


def demo_aggregations(db) -> None:
    print_section("Agrégation 1 - Nombre de livres par auteur")
    results = aggregations.books_count_by_author(db)
    for row in results:
        print(f"{row['auteur']:<30} {row['nombre_livres']}")

    print_section("Agrégation 2 - Livres empruntés non rendus")
    results = aggregations.books_currently_borrowed(db)
    for row in results:
        retard = "EN RETARD" if row["en_retard"] else "dans les délais"
        print(
            f"- {row['titre_livre']} | emprunté par {row['emprunteur']} "
            f"| {retard}"
        )


def demo_indexes(db) -> None:
    print_section("Index existants sur la collection 'books'")
    for index in indexes.list_indexes(db):
        print(f"- {index['name']} : {index.get('key')}")

    print_section("Vérification via explain() - recherche par titre")
    plan = indexes.explain_title_search(db, "1984")
    stage = plan.get("queryPlanner", {}).get("winningPlan", {})
    print(f"Plan d'exécution retenu : {stage}")


def main() -> None:
    db = get_database()
    print(f"Connexion établie à la base '{db.name}'.")

    demo_crud(db)
    demo_aggregations(db)
    demo_indexes(db)

    close_connection()
    print("\nDémonstration terminée.")


if __name__ == "__main__":
    main()
