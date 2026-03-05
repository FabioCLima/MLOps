import argparse
import sys

from loguru import logger

# ─────────────────────────────────────────────
# 1. CONFIGURAÇÃO DO LOGURU
# ─────────────────────────────────────────────

# Remove o handler padrão (evita duplicatas)
logger.remove()

# Handler no terminal (stdout) – mostra apenas INFO ou acima
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
)

# Handler em arquivo com rotação automática
logger.add(
    "logs/pipeline.log",
    level="DEBUG",              # salva tudo, inclusive DEBUG
    rotation="10 MB",           # cria novo arquivo ao atingir 10 MB
    retention="7 days",         # mantém logs dos últimos 7 dias
    compression="zip",          # comprime arquivos antigos
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


# ─────────────────────────────────────────────
# 2. CONFIGURAÇÃO DO ARGPARSE
# ─────────────────────────────────────────────

parser = argparse.ArgumentParser(
    description="Exemplo didático: soma dois números com argparse + loguru"
)

parser.add_argument(
    "--number_1",
    type=float,
    help="Primeiro número (obrigatório)",
    required=True,
)
parser.add_argument(
    "--number_2",
    type=int,
    help="Segundo número (opcional, padrão = 3)",
    required=False,
    default=3,
)

args = parser.parse_args()


# ─────────────────────────────────────────────
# 3. LÓGICA PRINCIPAL
# ─────────────────────────────────────────────

def soma(a: float, b: int) -> float:
    """Soma dois números e retorna o resultado."""
    return a + b


logger.info("Script iniciado")
logger.debug(f"Argumentos recebidos → number_1={args.number_1}, number_2={args.number_2}")

# Exemplo dos diferentes níveis de log
logger.debug("Este nível aparece SOMENTE no arquivo (muito detalhado)")
logger.info("Este nível aparece no terminal e no arquivo")
logger.warning("Aviso: algo merece atenção, mas não é um erro")

# Validação simples dos argumentos
if args.number_1 < 0:
    logger.error("number_1 não pode ser negativo!")
    sys.exit(1)

resultado = soma(args.number_1, args.number_2)

logger.info(f"{args.number_1} + {args.number_2} = {resultado}")
logger.info("Script finalizado com sucesso")
