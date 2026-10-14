# docs/generate_lineage.py — writes the dbt lineage as a Mermaid diagram into README.md,
# from dbt/target/manifest.json (run `dbt parse` or `dbt build` first). GitHub renders it.
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MANIFEST = ROOT / "dbt" / "target" / "manifest.json"
README = ROOT / "README.md"
START, END = "<!-- lineage:start -->", "<!-- lineage:end -->"

# Columns of the diagram, left to right
GROUPS = [
    ("sources", "Sources (raw)"),
    ("seeds", "Seeds"),
    ("staging", "Staging"),
    ("intermediate", "Intermediate"),
    ("marts", "Marts"),
]


def group_of(node: dict) -> str:
    if node["resource_type"] == "source":
        return "sources"
    if node["resource_type"] == "seed":
        return "seeds"
    return node["fqn"][1]  # models/<layer>/...


def label(node: dict) -> str:
    if node["resource_type"] == "source":
        return f"raw.{node['name']}"
    return node["name"]


def mermaid(manifest: dict) -> str:
    nodes = {
        uid: n for uid, n in {**manifest["nodes"], **manifest["sources"]}.items()
        if n["resource_type"] in ("model", "seed", "source")
    }
    ids = {uid: f"n{i}" for i, uid in enumerate(sorted(nodes))}

    lines = ["```mermaid", "flowchart LR"]
    for key, title in GROUPS:
        members = sorted(uid for uid, n in nodes.items() if group_of(n) == key)
        if not members:
            continue
        lines.append(f'    subgraph {key}["{title}"]')
        lines += [f'        {ids[uid]}["{label(nodes[uid])}"]' for uid in members]
        lines.append("    end")
    for uid, node in sorted(nodes.items()):
        for parent in node.get("depends_on", {}).get("nodes", []):
            if parent in ids:
                lines.append(f"    {ids[parent]} --> {ids[uid]}")
    lines.append("```")
    return "\n".join(lines)


def main() -> None:
    if not MANIFEST.exists():
        sys.exit(f"{MANIFEST} not found - run `dbt parse` in dbt/ first")
    diagram = mermaid(json.loads(MANIFEST.read_text(encoding="utf-8")))

    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        sys.exit(f"Add {START} and {END} markers to README.md")
    block = f"{START}\n{diagram}\n{END}"
    README.write_text(
        re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S),
        encoding="utf-8",
    )
    print("README.md lineage updated")


if __name__ == "__main__":
    main()
