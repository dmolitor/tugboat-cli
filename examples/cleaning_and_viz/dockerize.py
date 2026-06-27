from tugboat_cli import build, create, binderize
from pathlib import Path

CUR_PROJECT = Path("./examples/cleaning_and_viz/").resolve()

create(
    project = CUR_PROJECT,
    FROM = None,
    exclude = [".dockerignore", "Dockerfile", ".DS_Store", "dockerize.py", "*.csv"],
    verbose = False,
    detect_r = True,
    detect_python = True
)

build(dockerfile=CUR_PROJECT / "Dockerfile", image_name="clean_and_viz", build_context=CUR_PROJECT)

binderize(project=CUR_PROJECT, detect_r=True, detect_python=True)