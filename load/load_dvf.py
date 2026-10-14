# load/load_dvf.py — loads every data/*.csv.gz into raw.dvf, untouched
import csv
import gzip
import os
import sys
from pathlib import Path

import psycopg

DSN = os.environ.get(
    "DVF_DSN", "postgresql://analytics:analytics@localhost:5432/lyon_immo"
)
DATA_DIR = Path(__file__).parent.parent / "data"


def read_header(path: Path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def main() -> None:
    files = sorted(DATA_DIR.glob("*.csv.gz"))
    if not files:
        sys.exit(f"No .csv.gz files in {DATA_DIR} - run load/download_dvf.py first")

    # Every column is created as text: types are dbt's job, not the loader's
    columns = read_header(files[0])
    cols_ddl = ", ".join(f'"{c}" text' for c in columns)
    col_list = ", ".join(f'"{c}"' for c in columns)

    try:
        with psycopg.connect(DSN) as conn, conn.cursor() as cur:
            cur.execute("create schema if not exists raw")
            cur.execute("drop table if exists raw.dvf")
            cur.execute(
                f"create table raw.dvf ({cols_ddl}, _source_file text,"
                f" _loaded_at timestamptz default now())"
            )

            for path in files:
                if read_header(path) != columns:
                    raise ValueError(f"Schema drift in {path.name}")
                with gzip.open(path, "rb") as f, cur.copy(
                    f"copy raw.dvf ({col_list}) from stdin"
                    f" with (format csv, header true, encoding 'UTF8')"
                ) as copy:
                    while chunk := f.read(1 << 20):
                        copy.write(chunk)
                cur.execute(
                    "update raw.dvf set _source_file = %s where _source_file is null",
                    (path.name,),
                )
                print(f"Loaded {path.name}: {cur.rowcount} rows")

            cur.execute("select count(*) from raw.dvf")
            print(f"raw.dvf total: {cur.fetchone()[0]} rows")
    except (psycopg.Error, ValueError, OSError) as e:
        sys.exit(f"Load failed: {e}")


if __name__ == "__main__":
    main()
