#!/usr/bin/env python
import argparse
import pathlib
import sys

from loguru import logger

import wandb
from exercises.log_function import setup_logger

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
PROJECT_NAME = "exercise_1"
JOB_TYPE = "upload_file"
GROUP_EXPERIMENTATION = "experiment_ex1"


# ─────────────────────────────────────────────
# COMPONENT LOGIC
# ─────────────────────────────────────────────
def upload_artifact(args):
    """Upload a local file as a versioned artifact to Weights & Biases.

    Validates the input file, initializes a W&B run, creates an artifact with
    the provided metadata, attaches the file, and logs it to the run.

    Args:
        args (argparse.Namespace): Parsed CLI arguments with the following fields:
            input_file (pathlib.Path): Path to the local file to upload.
            artifact_name (str): Name to assign to the W&B artifact.
            artifact_type (str): Type category for the artifact (e.g. ``"dataset"``, ``"model"``).
            artifact_description (str): Human-readable description of the artifact.

    Raises:
        SystemExit: If ``args.input_file`` does not exist on disk.
    """
    # Validation - args.input_file from CLI it is pathlib.Path object
    if not args.input_file.is_file():
        logger.error(f"File not found: {args.input_file}")
        sys.exit(1)

    logger.info(f"Input file found: {args.input_file}")
    logger.info(f"Creating W&B run in project'{PROJECT_NAME}'")

    # Initialize the W&B run — job_type describes what this component does
    run = wandb.init(
        project=PROJECT_NAME, job_type=JOB_TYPE, group=GROUP_EXPERIMENTATION
    )

    # Create and populate the artifact
    artifact = wandb.Artifact(
        name=args.artifact_name,
        type=args.artifact_type,
        description=args.artifact_description,
    )

    # Attach the file and log the artifact — W&B handles versioning and tracking
    artifact.add_file(str(args.input_file))
    run.log_artifact(artifact)

    # Explicit finish — important in automated pipelines
    run.finish()

    logger.info(f"Artifact '{args.artifact_name}' uploaded successfully")


if __name__ == "__main__":
    # ─────────────────────────────────────────────
    #          ARGPARSE CONFIGURATION
    # ─────────────────────────────────────────────

    setup_logger()  # config logger before anything else

    parser = argparse.ArgumentParser(
        description="Upload an artifact to W&B", fromfile_prefix_chars="@"
    )

    parser.add_argument(
        "--input_file", type=pathlib.Path, help="Path to the input file", required=True
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

    upload_artifact(args)
