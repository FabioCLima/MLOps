from pathlib import Path

# 1. Diretório raiz
ROOT_DIR = Path(__file__).resolve().parent.parent

# 2. Define os subdiretórios
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
WANDB_DIR = ROOT_DIR / "wandb"
SRC_DIR = ROOT_DIR / "src"

# 3. Opcional: Garante que eles existam ao rodar o projeto
for directory in [DATA_DIR, LOGS_DIR, WANDB_DIR, SRC_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    print(ROOT_DIR)
