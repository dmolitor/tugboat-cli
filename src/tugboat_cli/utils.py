import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import List


class DockerNotFoundError(Exception):
    pass

class RNotFoundError(Exception):
    pass

def _stop_if_docker_not_installed() -> None:
    """Ensure Docker is available"""
    if not shutil.which("docker"):
        raise DockerNotFoundError(
            "Visit https://docs.docker.com/get-docker/ to get started!"
        )

def _stop_if_r_not_installed() -> None:
    """Ensure R is available"""
    if not shutil.which("Rscript"):
        raise RNotFoundError(
            "Rscript command not found. Visit https://www.r-project.org/ to get started!"
        )

def _to_r_literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, Path):
        value = str(value)
    if isinstance(value, str):
        value = (
            value
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )
        return f'"{value}"'
    if isinstance(value, (list, tuple)):
        values = ", ".join(_to_r_literal(x) for x in value)
        return f"c({values})"
    raise TypeError(
        f"Cannot convert {type(value).__name__} to an R literal."
    )

def _r_lockfile_with_temp_libpath(
    project: str | Path,
    **renv_kwargs
):
    _stop_if_r_not_installed()
    project = Path(project).resolve()
    rscript = shutil.which("Rscript")
    renv_args = ", ".join(
        f"{key} = {_to_r_literal(value)}"
        for key, value in renv_kwargs.items()
    )
    r_code = f"""
install.packages("pak", repos = sprintf(
"https://r-lib.github.io/p/pak/stable/%s/%s/%s",
.Platform$pkgType,
R.Version()$os,
R.Version()$arch
))

pak::pkg_install("tugboat")

# Initialize renv.lock
lockfile <- tugboat:::init_renv(project = "{str(project)}", {renv_args})
    """
    with tempfile.TemporaryDirectory(prefix="r-lib-") as library:
        env = os.environ.copy()
        env["R_LIBS_USER"] = library
        subprocess.run(
            [rscript, "-e", r_code],
            env=env,
            check=True,
            text=True,
            capture_output=False,
        )
