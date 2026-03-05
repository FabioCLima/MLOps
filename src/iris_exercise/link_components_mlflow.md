# Conectando Componentes com MLflow Pipelines

## Visão Geral

Um pipeline MLflow é uma sequência de **componentes independentes** conectados
por **artefatos versionados no W&B**. Cada componente tem seu próprio ambiente
(`conda.yml`) e ponto de entrada (`MLproject`), garantindo isolamento e
reprodutibilidade.

---

## Estrutura do Projeto

```
iris_exercise/              ← raiz do pipeline (orquestrador)
├── main.py                 ← orquestrador (Hydra + mlflow.run)
├── config.yaml             ← configurações do pipeline (Hydra)
├── conda.yml               ← dependências do orquestrador
├── MLproject               ← entry point do pipeline completo
│
├── download_data/          ← componente 1
│   ├── download_data.py
│   ├── conda.yml
│   └── MLproject
│
└── process_data/           ← componente 2
    ├── run.py
    ├── conda.yml
    └── MLproject
```

---

## Como os Componentes se Conectam

```
[config.yaml]
     │
     ▼
[main.py]  ← orquestrador Hydra
     │
     ├─── mlflow.run("download_data") ──► download_data.py
     │         │  parâmetros: file_url,      │
     │         │  artifact_name, ...         │ faz upload
     │         │                             ▼
     │         │                       [W&B Artifact]
     │         │                       iris.csv:latest
     │         │                             │
     └─── mlflow.run("process_data") ────────┘
               │  parâmetros: input_artifact  │
               │  = "iris.csv:latest"         │ faz download
               │                             ▼
               │                       run.py processa
               │                       t-SNE + salva
               │                             │ faz upload
               │                             ▼
               │                       [W&B Artifact]
               └──────────────────► cleaned_data:latest
```

---

## Peças-Chave

### 1. `MLproject` (raiz) — define o pipeline como um todo

```yaml
name: iris_pipeline
conda_env: conda.yml

entry_points:
  main:
    parameters:
      hydra_options:
        type: str
        default: ""
    command: >-
      python main.py {hydra_options}
```

O parâmetro `hydra_options` permite sobrescrever qualquer valor do `config.yaml`
em tempo de execução sem editar o arquivo.

### 2. `config.yaml` — configuração via Hydra

```yaml
main:
  project_name: iris_pipeline
  experiment_name: dev       # sobrescrito com -P hydra_options="main.experiment_name=prod"

data:
  file_url: https://...      # URL do dataset
```

O Hydra injeta automaticamente esse dicionário na função `run_pipeline(config)`.

### 3. `main.py` — orquestrador

```python
@hydra.main(config_name="config")
def run_pipeline(config: DictConfig):
    # Agrupa todas as runs no mesmo experimento W&B
    os.environ["WANDB_PROJECT"] = config["main"]["project_name"]
    os.environ["WANDB_RUN_GROUP"] = config["main"]["experiment_name"]

    root_path = hydra.utils.get_original_cwd()  # path estável independente do Hydra

    # Passo 1 — baixa dado bruto e loga no W&B
    mlflow.run(os.path.join(root_path, "download_data"), "main", parameters={...})

    # Passo 2 — consome artefato do passo 1 e produz dado limpo
    mlflow.run(os.path.join(root_path, "process_data"), "main", parameters={
        "input_artifact": "iris.csv:latest",  # ← link entre os passos!
        ...
    })
```

**O link entre componentes é o nome do artefato W&B.**
O `download_data` publica `iris.csv`, e o `process_data` o consome via
`run.use_artifact("iris.csv:latest")`.

### 4. `MLproject` de cada componente — isola o ambiente

```yaml
# download_data/MLproject
name: download_data
conda_env: conda.yml          # ambiente próprio deste componente

entry_points:
  main:
    parameters:
      file_url:    { type: uri }
      artifact_name: { type: str }
      artifact_type: { type: str, default: raw_data }
      artifact_description: { type: str }
    command: >-
      python download_data.py
        --file_url {file_url}
        --artifact_name {artifact_name}
        --artifact_type {artifact_type}
        --artifact_description {artifact_description}
```

O MLflow substitui `{file_url}` etc. pelos valores passados via `parameters={}` no `main.py`.

---

## Comandos

```bash
# Executar o pipeline completo (da raiz iris_exercise)
mlflow run . --env-manager=local

# Trocar o experimento em runtime sem editar config.yaml
mlflow run . --env-manager=local -P hydra_options="main.experiment_name=prod"

# Executar um componente isolado para teste
mlflow run download_data --env-manager=local \
  -P file_url="https://..." \
  -P artifact_name="iris.csv" \
  -P artifact_type="raw_data" \
  -P artifact_description="Raw iris dataset"
```

---

## Por que `env_manager="local"` no `mlflow.run()`?

Quando você usa `uv` (ou virtualenv próprio), passa `env_manager="local"` tanto
no CLI (`--env-manager=local`) quanto no código Python (`mlflow.run(..., env_manager="local")`).
Isso diz ao MLflow: *"não tente criar ambiente conda, use o Python ativo"*.

Em produção com conda instalado, basta remover esse parâmetro e o MLflow
gerencia o ambiente automaticamente a partir do `conda.yml`.

---

## Fluxo de Dados no W&B

Após executar o pipeline, no W&B você verá na aba **Artifacts > Graph View**:

```
[Run: download_data] ──produz──► iris.csv:v0
                                      │
                                   consome
                                      │
[Run: process_data]  ──produz──► cleaned_data:v0
```

Esse grafo de linhagem é criado automaticamente pelo W&B ao usar
`run.log_artifact()` e `run.use_artifact()`.
