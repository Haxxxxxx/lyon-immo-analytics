# metabase/create_dashboards.py — builds every dashboard in metabase/dashboards/ through
# Metabase's API. Re-runnable: archives the previous cards and dashboards of the collection first.
#
# Usage: MB_API_KEY=mb_xxx python metabase/create_dashboards.py
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

from dashboards import annonce, budget, louer_acheter, marche

MB_URL = os.environ.get("MB_URL", "http://localhost:3000").rstrip("/")
MB_API_KEY = os.environ.get("MB_API_KEY")
DB_NAME = "lyon_immo"
COLLECTION = "Lyon Immo Analytics"

DASHBOARDS = [marche.DASHBOARD, budget.DASHBOARD, annonce.DASHBOARD, louer_acheter.DASHBOARD]


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


def template_tags(query: str, params: list[dict]) -> dict:
    # A card gets a template tag for every dashboard filter its SQL references
    tags = {}
    for p in params:
        if "{{" + p["slug"] + "}}" not in query:
            continue
        tag = {
            "id": str(uuid.uuid4()),
            "name": p["slug"],
            "display-name": p["name"],
            "type": p["kind"],
            "required": p["default"] is not None,
        }
        if p["default"] is not None:
            tag["default"] = p["default"]
        tags[p["slug"]] = tag
    return tags


def dashboard_parameter(p: dict) -> dict:
    param = {
        "id": p["slug"],
        "slug": p["slug"],
        "name": p["name"],
        "type": "number/=" if p["kind"] == "number" else "string/=",
        "sectionId": "number" if p["kind"] == "number" else "string",
    }
    if p["default"] is not None:
        param["default"] = [p["default"]]
        param["required"] = True
    if p.get("values"):
        param["values_query_type"] = "list"
        param["values_source_type"] = "static-list"
        param["values_source_config"] = {"values": p["values"]}
    return param


def create_card(spec: dict, params: list[dict], db_id: int, collection_id: int) -> tuple[int, list[str]]:
    tags = template_tags(spec["query"], params)
    created = api("POST", "/card", {
        "name": spec["name"],
        "display": spec["display"],
        "collection_id": collection_id,
        "dataset_query": {
            "type": "native",
            "database": db_id,
            "native": {"query": spec["query"], "template-tags": tags},
        },
        "visualization_settings": spec["viz"],
    })
    return created["id"], list(tags)


def create_dashboard(spec: dict, db_id: int, collection_id: int) -> int:
    dashboard = api("POST", "/dashboard", {
        "name": spec["name"],
        "description": spec["description"],
        "collection_id": collection_id,
    })

    dashcards = []
    for i, block in enumerate(spec["layout"], start=1):
        item = block["item"]
        dashcard = {
            "id": -i,
            "row": block["row"], "col": block["col"],
            "size_x": block["width"], "size_y": block["height"],
        }
        if "text" in item:
            dashcard |= {
                "card_id": None,
                "visualization_settings": {
                    "virtual_card": {
                        "name": None, "display": "text", "archived": False,
                        "dataset_query": {}, "visualization_settings": {},
                    },
                    "text": item["text"],
                },
            }
        else:
            card_id, tags = create_card(item, spec["parameters"], db_id, collection_id)
            dashcard |= {
                "card_id": card_id,
                "visualization_settings": {},
                "parameter_mappings": [
                    {"parameter_id": tag, "card_id": card_id,
                     "target": ["variable", ["template-tag", tag]]}
                    for tag in tags
                ],
            }
        dashcards.append(dashcard)

    api("PUT", f"/dashboard/{dashboard['id']}", {
        "parameters": [dashboard_parameter(p) for p in spec["parameters"]],
        "dashcards": dashcards,
    })
    return dashboard["id"]


def main() -> None:
    if not MB_API_KEY:
        sys.exit("Set MB_API_KEY (Metabase > Admin > Settings > Authentication > API keys)")

    db_id = find_database_id()
    collection_id = reset_collection()
    for spec in DASHBOARDS:
        dashboard_id = create_dashboard(spec, db_id, collection_id)
        print(f"{spec['name']}: {MB_URL}/dashboard/{dashboard_id}")


if __name__ == "__main__":
    main()
