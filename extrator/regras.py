from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    yaml = None

DEFAULT = {
    "historico_debito": ["JUROS", "IOF", "TARIFA", "SEGURO", "MULTA", "ENCARGO"],
    "historico_credito": ["AMORTIZACAO", "PAGAMENTO", "LIQUIDACAO", "ESTORNO", "DEVOLUCAO"],
    "historico_transferencia": ["TRANSF", "TRANSFERENCIA"],
}
# diretorio base do projeto
def get_base_dir():
    """
    Retorna o diretório base do projeto.

    - Se rodando como executável (PyInstaller): pasta onde está o .exe
    - Se rodando como script: raiz do projeto (um nível acima do módulo)
    """
    if getattr(sys, "frozen", False):
        # Executável (.exe)
        return Path(sys.executable).resolve().parent
    else:
        # Script Python — ajusta conforme sua estrutura
        return Path(__file__).resolve().parents[1]


def carregar_regras():
    """
    Lê config/regras.yaml se existir; senão usa DEFAULT.
    base_dir = pasta onde está o executável (ou o projeto).
    """
    base_dir = get_base_dir()
    cfg = base_dir / "config" / "regras.yaml"
    if yaml is None or not cfg.exists():
        return DEFAULT

    with open(cfg, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # fallback para default
    out = DEFAULT.copy()
    out.update({k: v for k, v in data.items() if isinstance(v, list)})
    return out
