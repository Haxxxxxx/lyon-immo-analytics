# metabase/create_dashboard.py — builds the "Lyon Immo" dashboard through Metabase's API.
# Re-runnable: archives the previous version of the collection's cards and dashboard first.
#
# Usage: MB_API_KEY=mb_xxx python metabase/create_dashboard.py
import json
import os
import sys
import urllib.error
import urllib.request

MB_URL = os.environ.get("MB_URL", "http://localhost:3000").rstrip("/")
MB_API_KEY = os.environ.get("MB_API_KEY")
DB_NAME = "lyon_immo"
COLLECTION = "Lyon Immo Analytics"

LATEST_YEAR = "(select max(annee) from marts.fct_prix_m2_annuel)"


def col(title: str, suffix: str = "") -> dict:
    # French number format: 4 808 rather than 4,808
    settings = {"column_title": title, "number_separators": ", "}
    if suffix:
        settings["suffix"] = suffix
    return settings


def columns(**cols: dict) -> dict:
    return {"column_settings": {json.dumps(["name", name]): c for name, c in cols.items()}}


CARDS = {
    "prix_par_arrondissement": {
        "name": "Prix médian au m² par arrondissement (appartements, dernière année)",
        "display": "row",
        "query": f"""
select arrondissement, round(prix_m2_median) as prix_m2_median, nb_ventes
from marts.fct_prix_m2_annuel
where type_local = 'Appartement' and annee = {LATEST_YEAR}
order by prix_m2_median desc""",
        "viz": {
            "graph.dimensions": ["arrondissement"],
            "graph.metrics": ["prix_m2_median"],
            "graph.show_values": True,
            "graph.x_axis.title_text": "Arrondissement",
            "graph.y_axis.title_text": "Prix médian (€/m²)",
            **columns(prix_m2_median=col("Prix médian", " €/m²")),
        },
    },
    "evolution_prix": {
        "name": "Évolution du prix médian au m² (appartements)",
        "display": "line",
        "query": """
select make_date(annee, 1, 1) as annee, arrondissement, round(prix_m2_median) as prix_m2_median
from marts.fct_prix_m2_annuel
where type_local = 'Appartement'
order by annee, arrondissement""",
        "viz": {
            "graph.dimensions": ["annee", "arrondissement"],
            "graph.metrics": ["prix_m2_median"],
            "graph.x_axis.title_text": "Année",
            "graph.y_axis.title_text": "Prix médian (€/m²)",
            **columns(prix_m2_median=col("Prix médian", " €/m²")),
        },
    },
    "volume_mensuel": {
        "name": "Volume mensuel de ventes (logements)",
        "display": "bar",
        "query": """
select mois, sum(nb_ventes) as nb_ventes
from marts.fct_prix_m2_mensuel
group by mois
order by mois""",
        "viz": {
            "graph.dimensions": ["mois"],
            "graph.metrics": ["nb_ventes"],
            "graph.x_axis.title_text": "Mois",
            "graph.y_axis.title_text": "Nombre de ventes",
            **columns(nb_ventes=col("Ventes")),
        },
    },
    "comparaison_types": {
        "name": "Appartements vs maisons (dernière année)",
        "display": "table",
        "query": f"""
select
    arrondissement,
    max(nb_ventes)                    filter (where type_local = 'Appartement') as ventes_appartements,
    round(max(prix_m2_median) filter (where type_local = 'Appartement'))         as prix_m2_appartement,
    round(max(surface_mediane) filter (where type_local = 'Appartement'))        as surface_appartement,
    coalesce(max(nb_ventes)           filter (where type_local = 'Maison'), 0)  as ventes_maisons,
    round(max(prix_m2_median) filter (where type_local = 'Maison'))              as prix_m2_maison,
    round(max(surface_mediane) filter (where type_local = 'Maison'))             as surface_maison
from marts.fct_prix_m2_annuel
where annee = {LATEST_YEAR}
group by code_commune, arrondissement
order by code_commune""",
        "viz": columns(
            arrondissement=col("Arrondissement"),
            ventes_appartements=col("Ventes appartements"),
            prix_m2_appartement=col("Prix médian appartement", " €/m²"),
            surface_appartement=col("Surface médiane appartement", " m²"),
            ventes_maisons=col("Ventes maisons"),
            prix_m2_maison=col("Prix médian maison", " €/m²"),
            surface_maison=col("Surface médiane maison", " m²"),
        ),
    },
}

INSIGHT = """## Ce qu'il faut retenir

**Le marché lyonnais s'est corrigé après la hausse des taux.** Le volume de ventes de logements a chuté de **29 %** entre 2021 et 2024 (8 266 → 5 894 ventes), et le prix médian des appartements a reculé d'environ **12 %** entre 2022 et 2025 (5 088 → 4 471 €/m²). 2025 montre une reprise des volumes (+16 %) sans remontée des prix.

**Lyon 6e reste l'arrondissement le plus cher** (≈ 5 470 €/m² en 2025, +22 % vs la médiane de la ville), Lyon 5e et 9e les plus accessibles (≈ 3 700 €/m²).

*Source : DVF géolocalisées 2021–2025 (Etalab). Ventes contenant un seul logement, hors VEFA ; ~1 % de prix aberrants exclus. Médianes, pas moyennes.*"""

# Layout on Metabase's 24-column grid as (card, row, col, width, height):
# insight on top, two charts side by side, then full-width time series and table
INSIGHT_HEIGHT = 7
LAYOUT = [
    ("prix_par_arrondissement", 7, 0, 12, 9),
    ("evolution_prix", 7, 12, 12, 9),
    ("volume_mensuel", 16, 0, 24, 7),
    ("comparaison_types", 23, 0, 24, 7),
]


def api(method: str, path: str, body: dict | None = None):
    req = urllib.request.Request(
        f"{MB_URL}/api{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"X-API-KEY": MB_API_KEY, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} failed ({e.code}): {e.read().decode()[:500]}")
    return json.loads(raw) if raw else None


def find_database_id() -> int:
    dbs = api("GET", "/database")
    dbs = dbs["data"] if isinstance(dbs, dict) else dbs
    for db in dbs:
        if db["details"].get("dbname") == DB_NAME:
            return db["id"]
    sys.exit(f"No Metabase database pointing at '{DB_NAME}' - connect it in Admin first")


def reset_collection() -> int:
    for coll in api("GET", "/collection"):
        if coll.get("name") == COLLECTION and not coll.get("archived"):
            items = api("GET", f"/collection/{coll['id']}/items")["data"]
            for item in items:
                if item["model"] in ("card", "dashboard"):
                    api("PUT", f"/{item['model']}/{item['id']}", {"archived": True})
            return coll["id"]
    return api("POST", "/collection", {"name": COLLECTION, "color": "#509EE3"})["id"]


def main() -> None:
    if not MB_API_KEY:
        sys.exit("Set MB_API_KEY (Metabase > Admin > Settings > Authentication > API keys)")

    db_id = find_database_id()
    collection_id = reset_collection()

    card_ids = {}
    for key, card in CARDS.items():
        created = api("POST", "/card", {
            "name": card["name"],
            "display": card["display"],
            "collection_id": collection_id,
            "dataset_query": {
                "type": "native",
                "database": db_id,
                "native": {"query": card["query"].strip()},
            },
            "visualization_settings": card["viz"],
        })
        card_ids[key] = created["id"]
        print(f"Card {created['id']}: {card['name']}")

    dashboard = api("POST", "/dashboard", {
        "name": "Marché immobilier lyonnais",
        "description": "Prix au m² et volumes de ventes par arrondissement, DVF 2021–2025.",
        "collection_id": collection_id,
    })

    dashcards = [{
        "id": -1,
        "card_id": None,
        "row": 0, "col": 0, "size_x": 24, "size_y": INSIGHT_HEIGHT,
        "visualization_settings": {
            "virtual_card": {
                "name": None, "display": "text", "archived": False,
                "dataset_query": {}, "visualization_settings": {},
            },
            "text": INSIGHT,
        },
    }]
    for i, (key, row, column, width, height) in enumerate(LAYOUT, start=2):
        dashcards.append({
            "id": -i,
            "card_id": card_ids[key],
            "row": row, "col": column, "size_x": width, "size_y": height,
            "visualization_settings": {},
        })
    api("PUT", f"/dashboard/{dashboard['id']}", {"dashcards": dashcards})

    print(f"Dashboard: {MB_URL}/dashboard/{dashboard['id']}")


if __name__ == "__main__":
    main()
