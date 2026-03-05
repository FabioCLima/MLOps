"""Demo: Versioning Data and Artififacts in Weights & Biases"""

# Import Weight & Biases
import wandb

# Create an artifact (pretend it is the output of component)
with open("my_artifact.txt", "+w") as fp:
    fp.write("This is an example of an artifact")

# Upload to W&B
run = wandb.init(project="demo_artifact", group="experiment_1")

# create a artifact
artifact = wandb.Artifact(
    name="my_artifact.txt",
    type="data",
    description="This an example of artifact",
    metadata={"key_1": "value_1"},
)
artifact.add_file("my_artifact.txt")
run.log_artifact(artifact)
run.finish()
