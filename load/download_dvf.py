# load/download_dvf.py — downloads the Rhône (69) DVF géolocalisées files into data/
import sys
import urllib.request
from pathlib import Path

YEARS = range(2021, 2026)  # DVF is a rolling ~5-year window; 2020 is no longer published
URL = "https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/69.csv.gz"
DATA_DIR = Path(__file__).parent.parent / "data"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    for year in YEARS:
        target = DATA_DIR / f"dvf_69_{year}.csv.gz"
        if target.exists():
            print(f"Skip {target.name} (already there)")
            continue
        try:
            urllib.request.urlretrieve(URL.format(year=year), target)
        except OSError as e:
            target.unlink(missing_ok=True)
            sys.exit(f"Download failed for {year}: {e}")
        print(f"Downloaded {target.name} ({target.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
