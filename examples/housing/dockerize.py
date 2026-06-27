from tugboat_cli import build, create, binderize
from pathlib import Path

CUR_PROJECT = Path("./examples/housing/").resolve()

create(
    project=CUR_PROJECT,
    FROM=None,
    exclude=[".dockerignore", "Dockerfile", ".DS_Store", "dockerize.py", "*.png"],
    verbose=False,
    detect_r=False,
    detect_python=True,
)

build(dockerfile=CUR_PROJECT / "Dockerfile", image_name="housing", build_context=CUR_PROJECT)

binderize(project=CUR_PROJECT, detect_r=False, detect_python=True, urlpath="lab")
