from pathlib import Path

# .../seu_projeto/indices/bcb/config.py
INDICES_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = INDICES_DIR / "dados" / "bcb"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=csv"

SERIES = {
    20726: "serie_20726.csv",
    20727: "serie_20727.csv",
    20741: "serie_20741.csv",
}

TIMEOUT = 30