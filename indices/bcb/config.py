from pathlib import Path

# .../seu_projeto/indices/bcb/config.py
INDICES_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = INDICES_DIR / "dados" / "bcb"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=csv"

SERIES = {
    20769: "serie_20769.csv",
    20770: "serie_20770.csv",
}

TIMEOUT = 30