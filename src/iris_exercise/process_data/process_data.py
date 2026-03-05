#!/usr/bin/env python
"""
process_data.py

Component responsible for processing the raw iris dataset artifact from W&B.
Applies a t-SNE projection with 2 components, visualizes the result,
and uploads the enriched dataframe as a new versioned artifact.
Designed to run as a MLflow pipeline step after the download_data component.
"""

import argparse

import pandas as pd
import seaborn as sns
from logger_function import setup_logger
from loguru import logger
from sklearn.manifold import TSNE

import wandb

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
JOB_TYPE = "process_data"
OUTPUT_FILE = "clean_data.csv"


# ─────────────────────────────────────────────
# COMPONENT LOGIC
# ─────────────────────────────────────────────
def process_and_log_artifact(args):
    """
    Process raw iris data and upload the enriched dataset as a W&B artifact.

    Downloads the input artifact from W&B, applies t-SNE dimensionality
    reduction, logs the 2D projection plot, and uploads the resulting
    dataframe (with t-SNE columns added) as a new artifact.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments containing:
        - input_artifact (str): Fully-qualified W&B artifact name (e.g. iris.csv:latest).
        - artifact_name (str): Name to assign to the output artifact.
        - artifact_type (str): Type category of the output artifact.
        - artifact_description (str): Human-readable description of the output artifact.
    """
    run = wandb.init(job_type=JOB_TYPE)

    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    iris = pd.read_csv(
        artifact_path,
        skiprows=1,
        names=("sepal_length", "sepal_width", "petal_length", "petal_width", "target"),
    )

    target_names = "setosa,versicolor,virginica".split(",")
    iris["target"] = [target_names[k] for k in iris["target"]]

    logger.info("Performing t-SNE projection")
    tsne = TSNE(n_components=2, init="pca", random_state=0)
    transf = tsne.fit_transform(iris.iloc[:, :4])

    iris["tsne_1"] = transf[:, 0]
    iris["tsne_2"] = transf[:, 1]

    g = sns.displot(iris, x="tsne_1", y="tsne_2", hue="target", kind="kde")

    logger.info("Uploading image to W&B")
    run.log({"t-SNE": wandb.Image(g.figure)})

    logger.info("Creating artifact")

    # index = False avoids a "new coluna" index be created withing csv datafile
    iris.to_csv(OUTPUT_FILE, index=False)

    artifact = wandb.Artifact(
        name=args.artifact_name,
        type=args.artifact_type,
        description=args.artifact_description,
    )
    artifact.add_file(OUTPUT_FILE)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    # Explicit finish - important in automated pipelines
    run.finish()


if __name__ == "__main__":
    # ─────────────────────────────────────────────
    #          ARGPARSE CONFIGURATION
    # ─────────────────────────────────────────────

    setup_logger()  # config logger before anything else
    parser = argparse.ArgumentParser(
        description="Process iris data with t-SNE and upload as a W&B artifact",
        fromfile_prefix_chars="@",
    )

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Fully-qualified name for the input artifact",
        required=True,
    )

    parser.add_argument(
        "--artifact_name", type=str, help="Name for the artifact", required=True
    )

    parser.add_argument(
        "--artifact_type", type=str, help="Type for the artifact", required=True
    )

    parser.add_argument(
        "--artifact_description",
        type=str,
        help="Description for the artifact",
        required=True,
    )

    args = parser.parse_args()

    process_and_log_artifact(args)
