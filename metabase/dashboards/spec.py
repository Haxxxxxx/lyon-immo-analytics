# Small helpers to describe Metabase cards, text boxes and filters as plain dicts.
import json

ARRONDISSEMENTS = [
    "Lyon 1er", "Lyon 2e", "Lyon 3e", "Lyon 4e", "Lyon 5e",
    "Lyon 6e", "Lyon 7e", "Lyon 8e", "Lyon 9e",
]


def col(title: str, suffix: str = "", decimals: int | None = None) -> dict:
    # French number format: 4 808 rather than 4,808
    settings = {"column_title": title, "number_separators": ", "}
    if suffix:
        settings["suffix"] = suffix
    if decimals is not None:
        settings["decimals"] = decimals
    return settings


def columns(**cols: dict) -> dict:
    return {"column_settings": {json.dumps(["name", name]): c for name, c in cols.items()}}


def card(name: str, display: str, query: str, viz: dict | None = None) -> dict:
    return {"name": name, "display": display, "query": query.strip(), "viz": viz or {}}


def bar_viz(dimension: str, metric: str, x_title: str, y_title: str, **metric_col) -> dict:
    return {
        "graph.dimensions": [dimension],
        "graph.metrics": [metric],
        "graph.show_values": True,
        "graph.x_axis.title_text": x_title,
        "graph.y_axis.title_text": y_title,
        **columns(**{metric: col(**metric_col)}),
    }


def number_param(slug: str, name: str, default: float | None = None) -> dict:
    return {"slug": slug, "name": name, "kind": "number", "default": default}


def list_param(slug: str, name: str, values: list[str], default: str | None = None) -> dict:
    return {"slug": slug, "name": name, "kind": "text", "values": values, "default": default}


def place(item: dict, row: int, col: int, width: int, height: int) -> dict:
    return {"item": item, "row": row, "col": col, "width": width, "height": height}


def text(markdown: str) -> dict:
    return {"text": markdown.strip()}
