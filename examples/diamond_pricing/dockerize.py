from tugboat_cli import build, create, binderize
from pathlib import Path

CUR_PROJECT = Path("./examples/diamond_pricing/").resolve()

create(
    project=CUR_PROJECT,
    FROM=None,
    exclude=[".dockerignore", "Dockerfile", ".DS_Store", "dockerize.py", "*.png"],
    verbose=False,
    detect_r=True,
    detect_python=False,
)

build(dockerfile=CUR_PROJECT / "Dockerfile", image_name="diamond_pricing", build_context=CUR_PROJECT)

binderize(project=CUR_PROJECT, detect_r=True, detect_python=False)
