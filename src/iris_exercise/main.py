"""
main.py — Orquestrador do pipeline iris_exercise.

Este módulo é o ponto de entrada do pipeline MLflow. Ele NÃO executa nenhuma
lógica de ML diretamente; sua responsabilidade é exclusivamente orquestrar os
componentes downstream (download_data, process_data) chamando-os via
`mlflow.run()`, passando os parâmetros necessários a cada um.

Ferramentas utilizadas
----------------------
- MLflow Projects  : isola cada componente em seu próprio processo/ambiente,
                     garantindo reprodutibilidade. Cada subdiretório
                     (download_data/, process_data/) possui seu próprio
                     MLproject e conda.yml.
- Hydra            : gerencia a configuração via config.yaml, permitindo
                     sobrescrever parâmetros pela linha de comando sem alterar
                     o código (ex: main.experiment_name=prod).
- Weights & Biases : rastreia experimentos, artefatos e métricas. As variáveis
                     de ambiente WANDB_PROJECT e WANDB_RUN_GROUP definidas aqui
                     fazem com que todos os runs filhos sejam automaticamente
                     agrupados sob o mesmo experimento no dashboard do W&B.

Como executar
-------------
    # A partir da raiz do projeto:
    uv run mlflow run src/iris_exercise --env-manager=local

    # Sobrescrevendo parâmetros Hydra (appended direto após o script):
    # O MLproject não usa parâmetros intermediários — overrides são passados
    # como argumentos posicionais que o Hydra interpreta diretamente.
    # Para isso, edite o config.yaml ou invoque o script manualmente:
    uv run python src/iris_exercise/main.py main.experiment_name=prod
"""
import os

import hydra
import mlflow
from omegaconf import DictConfig


# version_base=None preserva o comportamento do Hydra 1.1, evitando o
# DeprecationWarning introduzido no Hydra 1.2 sobre mudanças de comportamento
# futuras. config_path="." indica que config.yaml está no mesmo diretório
# deste arquivo.
@hydra.main(config_path=".", config_name="config", version_base=None)
def run_pipeline(config: DictConfig):
    """
    Orquestra o pipeline completo de dados iris.

    Esta função é chamada automaticamente pelo decorator @hydra.main, que
    injeta o objeto `config` populado a partir do config.yaml. A função
    define o contexto W&B via variáveis de ambiente e dispara cada etapa
    do pipeline sequencialmente usando `mlflow.run()`.

    Por que usar variáveis de ambiente para o W&B?
    ----------------------------------------------
    Cada componente (download_data, process_data) inicializa seu próprio
    `wandb.run` de forma independente. Ao definir WANDB_PROJECT e
    WANDB_RUN_GROUP antes de lançá-los, garantimos que todos esses runs
    sejam automaticamente associados ao mesmo projeto e grupo no W&B,
    sem precisar passar essas informações como argumento CLI para cada
    componente.

    Por que `hydra.utils.get_original_cwd()`?
    -----------------------------------------
    O Hydra muda o diretório de trabalho para um subdiretório de outputs/
    durante a execução (para isolar logs e artefatos por run). Por isso,
    caminhos relativos como "./download_data" deixariam de funcionar.
    `get_original_cwd()` retorna o diretório original de onde o comando
    foi executado, permitindo construir caminhos absolutos corretos para
    os componentes.

    Por que `env_manager="local"`?
    ------------------------------
    Instrui o MLflow a NÃO criar um novo ambiente conda/virtualenv para
    cada componente. Em vez disso, usa o ambiente Python já ativo. Útil
    durante desenvolvimento, pois evita overhead de criação de ambientes.
    Em produção ou CI, considere usar env_manager="conda" para isolamento
    total.

    Parameters
    ----------
    config : DictConfig
        Configuração Hydra carregada do config.yaml. Chaves esperadas:
        - main.project_name (str)   : Nome do projeto no W&B.
        - main.experiment_name (str): Grupo de runs no W&B (ex: "dev", "prod").
        - data.file_url (str)       : URL remota do CSV bruto do iris.
    """
    # Propaga o contexto do experimento W&B para todos os processos filhos.
    # Os componentes herdam essas variáveis de ambiente automaticamente.
    os.environ["WANDB_PROJECT"] = config["main"]["project_name"]
    os.environ["WANDB_RUN_GROUP"] = config["main"]["experiment_name"]

    # Captura o diretório original antes que o Hydra mude o cwd.
    # Necessário para construir caminhos absolutos para os componentes.
    root_path = hydra.utils.get_original_cwd()

    # ── Step 1: download_data ──────────────────────────────────────────────
    # Baixa o CSV bruto da URL configurada e registra como artefato no W&B.
    # O artefato resultante ("iris.csv:latest") será consumido pelo próximo step.
    _ = mlflow.run(
        os.path.join(root_path, "download_data"),
        "main",
        env_manager="local",
        parameters={
            "file_url": config["data"]["file_url"],
            "artifact_name": "iris.csv",
            "artifact_type": "raw_data",
            "artifact_description": "Input data",
        },
    )

    # ── Step 2: process_data ───────────────────────────────────────────────
    # Consome "iris.csv:latest" do W&B, aplica t-SNE e registra o dataset
    # enriquecido como novo artefato ("cleaned_data").
    # O sufixo ":latest" garante que sempre usamos a versão mais recente
    # do artefato produzido no step anterior.
    _ = mlflow.run(
        os.path.join(root_path, "process_data"),
        "main",
        env_manager="local",
        parameters={
            "input_artifact": "iris.csv:latest",
            "artifact_name": "cleaned_data",
            "artifact_type": "clean_data",
            "artifact_description": "Iris dataset with t-SNE components added",
        },
    )


if __name__ == "__main__":
    run_pipeline()
