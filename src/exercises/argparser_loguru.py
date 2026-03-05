# =============================================================================
# REVIEW: argparse + loguru
# Contexto: componente de um pipeline MLOps
# =============================================================================

# =====================
# 1. LOGURU — Logging
# =====================

import argparse
import sys

from loguru import logger

# --- Configuração básica ---
# Por padrão, loguru já loga no stderr com formatação colorida.
# Mas podemos customizar:

logger.remove()  # remove o handler padrão

# Adiciona handler no terminal com nível INFO
logger.add(sys.stderr, level="INFO")

# Adiciona handler em arquivo com rotação
logger.add(
    "logs/pipeline.log",
    level="DEBUG",
    rotation="10 MB",  # cria novo arquivo ao atingir 10MB
    retention="7 days",  # mantém logs dos últimos 7 dias
    compression="zip",  # comprime arquivos antigos
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

# --- Níveis de log ---
logger.debug("Detalhe interno — visível só em DEBUG")
logger.info("Pipeline iniciado")
logger.warning("Coluna com 30% de nulos — verifique")
logger.error("Falha ao carregar artefato")
logger.critical("Sem memória — abortando pipeline")

# --- Contexto estruturado com bind ---
# Útil para rastrear de qual componente veio o log
component_logger = logger.bind(component="preprocess", version="1.0")
component_logger.info("Iniciando pré-processamento")
component_logger.info("Shape do dataset: 1000 x 12")


# --- Capturar exceções com traceback completo ---
def divide(a, b):
    return a / b


try:
    divide(10, 0)
except ZeroDivisionError:
    logger.exception("Erro durante cálculo")  # loga traceback completo


# --- Decorator para logar entrada/saída de funções ---
@logger.catch  # captura qualquer exceção não tratada
def treinar_modelo(epochs: int, lr: float):
    logger.info(f"Treinando por {epochs} epochs com lr={lr}")
    # ... lógica de treino
    return {"accuracy": 0.92}


resultado = treinar_modelo(epochs=10, lr=0.001)
logger.info(f"Resultado: {resultado}")


def get_args():
    parser = argparse.ArgumentParser(
        description="Componente de treinamento do pipeline MLOps"
    )

    # --- Argumento posicional (obrigatório, sem flag) ---
    parser.add_argument(
        "input_artifact",
        type=str,
        help="Nome do artefato de entrada no W&B (ex: raw_data:latest)",
    )

    # --- Argumentos opcionais (com flag --) ---
    parser.add_argument(
        "--epochs",
        type=int,
        default=10,
        help="Número de épocas de treinamento (default: 10)",
    )

    parser.add_argument(
        "--learning_rate",
        type=float,
        default=0.001,
        help="Learning rate do otimizador (default: 0.001)",
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        default="trained_model",
        help="Nome do artefato de saída no W&B",
    )

    # --- Flag booleana ---
    parser.add_argument(
        "--verbose",
        action="store_true",  # se --verbose presente, args.verbose = True
        help="Ativa logs detalhados",
    )

    # --- Escolha restrita com choices ---
    parser.add_argument(
        "--model_type",
        type=str,
        choices=["random_forest", "logistic_regression", "xgboost"],
        default="random_forest",
        help="Tipo de modelo a treinar",
    )

    # --- Múltiplos valores com nargs ---
    parser.add_argument(
        "--features",
        nargs="+",  # aceita 1 ou mais valores
        type=str,
        default=["bill_length_mm", "flipper_length_mm"],
        help="Lista de features a usar (ex: --features col1 col2 col3)",
    )

    return parser.parse_args()


# ======================================
# 3. JUNTANDO OS DOIS — script completo
# ======================================

# Como um componente real de pipeline ficaria:


def main():
    # 1. Parse dos argumentos
    args = get_args()

    # 2. Ajusta nível de log conforme --verbose
    logger.remove()
    level = "DEBUG" if args.verbose else "INFO"
    logger.add(sys.stderr, level=level)
    logger.add("logs/train.log", level="DEBUG", rotation="5 MB")

    # 3. Loga os parâmetros recebidos (boa prática para rastreabilidade)
    logger.info("=== Parâmetros do componente ===")
    logger.info(f"Input artifact : {args.input_artifact}")
    logger.info(f"Model type     : {args.model_type}")
    logger.info(f"Epochs         : {args.epochs}")
    logger.info(f"Learning rate  : {args.learning_rate}")
    logger.info(f"Features       : {args.features}")
    logger.info(f"Output artifact: {args.output_artifact}")

    # 4. Lógica do componente...
    logger.debug("Baixando artefato do W&B...")
    # artifact = run.use_artifact(args.input_artifact)

    logger.info("Treinamento concluído")


# Execução: python review_argparse_loguru.py raw_data:latest
#           --model_type xgboost
#           --epochs 50
#           --learning_rate 0.01
#           --features bill_length_mm flipper_length_mm body_mass_g
#           --verbose

if __name__ == "__main__":
    main()


# ========================
# 4. RESUMO RÁPIDO
# ========================

# argparse
# --------
# add_argument("nome")          → posicional (obrigatório)
# add_argument("--nome")        → opcional com flag
# type=int/float/str            → converte automaticamente
# default=valor                 → valor se não passado
# choices=[...]                 → valida as opções permitidas
# nargs="+"                     → aceita lista de valores
# action="store_true"           → flag booleana
# parser.parse_args()           → retorna namespace com os valores

# loguru
# ------
# logger.add(sink, level, ...)  → configura destino do log
# logger.bind(key=val)          → adiciona contexto permanente
# logger.debug/info/warning...  → loga em diferentes níveis
# logger.exception(msg)         → loga traceback da exceção atual
# @logger.catch                 → decorator que captura exceções
# rotation / retention          → gerencia arquivos de log
