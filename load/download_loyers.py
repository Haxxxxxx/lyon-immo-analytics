# load/download_loyers.py — downloads the rent sources into data/loyers/
#   - ANIL "Carte des loyers": rent per m² from listings, by commune (latest edition only:
#     the methodology note says editions aren't comparable over time)
#   - Métropole de Lyon rent control: legal reference rents by IRIS, current period
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "loyers"

CARTE_DATASET = (
    "https://www.data.gouv.fr/api/1/datasets/"
    "carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-{year}/"
)
# One file per segment: all apartments, 1-2 rooms, 3+ rooms
CARTE_SEGMENTS = ("pred-app-", "pred-app12-", "pred-app3-")

ENCADREMENT_URL = (
    "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0"
    "&request=GetFeature&typename=metropole-de-lyon:car_care.carencadrmtloyer_{period}"
    "&outputFormat=CSV&SRSNAME=EPSG:4326"
)


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url) as resp:
        return resp.read()


def download_carte_des_loyers() -> None:
    # The edition for year N is published in December of year N
    for year in range(date.today().year, date.today().year - 3, -1):
        try:
            dataset = json.loads(fetch(CARTE_DATASET.format(year=year)))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            raise
        for segment in CARTE_SEGMENTS:
            url = next(
                r["url"] for r in dataset["resources"]
                if r["format"] == "csv" and segment in r["url"]
            )
            target = DATA_DIR / f"carte_loyers_{year}_{segment.strip('-').removeprefix('pred-')}.csv"
            target.write_bytes(fetch(url))
            print(f"Downloaded {target.name}")
        return
    sys.exit("No Carte des loyers edition found for the last 3 years")


def download_encadrement() -> None:
    # Periods run from November to October; try the newest one first
    year = date.today().year
    for start in (year, year - 1):
        period = f"{start}_{start + 1}"
        try:
            content = fetch(ENCADREMENT_URL.format(period=period))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            raise
        if content.startswith(b"FID,"):
            target = DATA_DIR / f"encadrement_{period}.csv"
            target.write_bytes(content)
            print(f"Downloaded {target.name}")
            return
    sys.exit("No rent control period found for this year or last year")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        download_carte_des_loyers()
        download_encadrement()
    except (OSError, StopIteration, json.JSONDecodeError) as e:
        sys.exit(f"Download failed: {e!r}")


if __name__ == "__main__":
    main()
