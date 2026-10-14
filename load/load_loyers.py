# load/load_loyers.py — loads data/loyers/ into raw.carte_loyers and raw.encadrement_loyers, untouched
import csv
import os
import sys
from pathlib import Path

import psycopg

DSN = os.environ.get(
    "DVF_DSN", "postgresql://analytics:analytics@localhost:5432/lyon_immo"
)
DATA_DIR = Path(__file__).parent.parent / "data" / "loyers"

# table -> (file pattern, delimiter, file encoding as Python and Postgres name it)
SOURCES = {
    "carte_loyers": ("carte_loyers_*.csv", ";", "cp1252", "WIN1252"),
    "encadrement_loyers": ("encadrement_*.csv", ",", "utf-8", "UTF8"),
}


def read_header(path: Path, delimiter: str, encoding: str) -> list[str]:
    with open(path, encoding=encoding, newline="") as f:
        return next(csv.reader(f, delimiter=delimiter))


def load_table(cur: psycopg.Cursor, table: str, pattern: str, delimiter: str,
               py_encoding: str, pg_encoding: str) -> None:
    files = sorted(DATA_DIR.glob(pattern))
    if not files:
        raise ValueError(f"No {pattern} in {DATA_DIR} - run load/download_loyers.py first")

    # Every column is created as text: types are dbt's job, not the loader's
    columns = read_header(files[0], delimiter, py_encoding)
    cols_ddl = ", ".join(f'"{c}" text' for c in columns)
    col_list = ", ".join(f'"{c}"' for c in columns)

    cur.execute(f"drop table if exists raw.{table}")
    cur.execute(
        f"create table raw.{table} ({cols_ddl}, _source_file text,"
        f" _loaded_at timestamptz default now())"
    )
    for path in files:
        if read_header(path, delimiter, py_encoding) != columns:
            raise ValueError(f"Schema drift in {path.name}")
        with open(path, "rb") as f, cur.copy(
            f"copy raw.{table} ({col_list}) from stdin with (format csv, header true,"
            f" delimiter '{delimiter}', encoding '{pg_encoding}')"
        ) as copy:
            while chunk := f.read(1 << 20):
                copy.write(chunk)
        cur.execute(
            f"update raw.{table} set _source_file = %s where _source_file is null",
            (path.name,),
        )
        print(f"Loaded {path.name}: {cur.rowcount} rows")


def main() -> None:
    try:
        with psycopg.connect(DSN) as conn, conn.cursor() as cur:
            cur.execute("create schema if not exists raw")
            for table, options in SOURCES.items():
                load_table(cur, table, *options)
    except (psycopg.Error, ValueError, OSError) as e:
        sys.exit(f"Load failed: {e}")


if __name__ == "__main__":
    main()
