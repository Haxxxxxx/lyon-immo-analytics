# Lyon Immo Analytics

Pipeline ELT sur les transactions immobilières lyonnaises (DVF) : Postgres, dbt, Metabase.

```
DVF géolocalisées (data.gouv.fr) → Postgres (raw) → dbt (staging → intermediate → marts, testé) → Metabase
```

## How to run

```bash
docker compose up -d                       # Postgres :5432, Metabase :3000
python -m venv .venv && .venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python load/download_dvf.py                # Rhône DVF 2021–2025 → data/
python load/load_dvf.py                    # data/*.csv.gz → raw.dvf, untouched
cd dbt && dbt seed && dbt build && cd ..   # models + tests
MB_API_KEY=mb_xxx python metabase/create_dashboard.py   # dashboard as code
```

## Modelling decisions

_TODO: multi-row sales, median vs average, outlier handling._
