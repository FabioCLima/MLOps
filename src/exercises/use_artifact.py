#!/usr/bin/env python
import argparse

from loguru import logger

import wandb
from exercises.log_function import setup_logger

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
PROJECT_NAME = "exercise_1"
JOB_TYPE = "use_file"
GROUP_EXPERIMENTATION = "experiment_ex1"


# ─────────────────────────────────────────────
# COMPONENT LOGIC
# ─────────────────────────────────────────────
def use_artifact(args):
    """Download and read a versioned artifact from Weights & Biases.

    Initializes a W&B run, fetches the artifact specified by name and version,
    downloads it locally, and prints its content to stdout.

    Args:
        args (argparse.Namespace): Parsed CLI arguments with the following fields:
            artifact_name (str): Name and version of the W&B artifact
                                 (e.g. ``"zen_of_python:latest"`` or ``"zen_of_python:v0"``).
    """
    logger.info(f"Creating W&B run in project '{PROJECT_NAME}'")

    # Initialize the W&B run — job_type describes what this component does
    run = wandb.init(
        project=PROJECT_NAME, job_type=JOB_TYPE, group=GROUP_EXPERIMENTATION
    )

    logger.info(f"Fetching artifact: {args.artifact_name}")

    # Retrieve the artifact metadata from W&B — does not download yet
    artifact = run.use_artifact(args.artifact_name)

    # Download the artifact content and get the local file path
    artifact_path = artifact.file()

    logger.info("Artifact content:")
    with open(artifact_path, "r") as fp:
        content = fp.read()
    print(content)

    # Explicit finish — important in automated pipelines
    run.finish()

    logger.info(f"Artifact '{args.artifact_name}' read successfully")


if __name__ == "__main__":
    # ─────────────────────────────────────────────
    #          ARGPARSE CONFIGURATION
    # ─────────────────────────────────────────────

    setup_logger()  # config logger before anything else

    parser = argparse.ArgumentParser(
        description="Use an artifact from W&B", fromfile_prefix_chars="@"
    )

    parser.add_argument(
        "--artifact_name",
        type=str,
        help="Name and version of W&B artifact (e.g. zen_of_python:latest)",
        required=True,
    )

    args = parser.parse_args()

    use_artifact(args)
