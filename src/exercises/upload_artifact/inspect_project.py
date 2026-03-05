import yaml

with open("src/upload_artifact/MLproject") as fp:
    d = yaml.safe_load(fp)

print(d)
