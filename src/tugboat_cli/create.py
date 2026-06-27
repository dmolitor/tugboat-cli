from pathlib import Path
import shutil
import subprocess
import sys
from tugboat.create import _generate, _dockerignore
from typing import Dict, List

from .utils import _r_lockfile_with_temp_libpath, _stop_if_r_not_installed


def _default_python_image() -> str:
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return f"python:{py_version}-slim"


def _default_r_image() -> str:
    _stop_if_r_not_installed()
    rscript = shutil.which("Rscript")
    result = subprocess.run(
        [
            rscript,
            "--vanilla",
            "-e",
            "cat(as.character(getRversion()))",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    r_version = result.stdout.strip()
    return f"posit/r-base:{'.'.join(r_version.split('.')[0:2])}-noble"


def _default_image(detect_r: bool) -> str:
    if detect_r:
        return _default_r_image()
    return _default_python_image()


def _dockerfile(
    detect_r: bool,
    detect_python: bool,
    project_name: str | None = None,
    project: str = str(Path(".").resolve()),
    FROM: str | None = None,
    optimize_pak: bool = True,
) -> str:
    """
    Render a Dockerfile string for the given project configuration.
    """
    if project_name is None:
        project_dir = f"/{Path(project).name}"
    else:
        project_dir = f"/{project_name}"
    if not FROM:
        FROM = _default_image(detect_r=detect_r)
    dock = f"FROM {FROM}"
    if detect_python:
        dock = dock + "\nCOPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/"
    if detect_r:
        dock = dock + "\nCOPY renv.lock renv.lock"
    dock = dock + f"""
COPY . {project_dir}
WORKDIR {project_dir}
"""
    if detect_r:
        dock = dock + """
RUN for d in /usr/local/lib/R/etc /usr/lib/R/etc; do \\
      mkdir -p "$d" 2>/dev/null || true; \\
      f="$d/Rprofile.site"; \\
      { echo "options(renv.config.pak.enabled = TRUE)" >> "$f" 2>/dev/null || true; } \\
    done
RUN R -e "install.packages('pak', repos = sprintf('https://r-lib.github.io/p/pak/stable/%s/%s/%s', .Platform[['pkgType']], R.Version()[['os']], R.Version()[['arch']]))"
"""
        if optimize_pak:
            dock = (
                dock
                + """RUN R -e "dist <- pak::system_r_platform_data()[['distribution']]; rel <- pak::system_r_platform_data()[['release']]; binary_url <- subset(pak::ppm_platforms(), distribution == dist & release == rel)[['binary_url']][1]; cran_binary_url <- if (!is.na(binary_url)) { sprintf('%s/__linux__/%s/latest', pak::ppm_repo_url(), binary_url)  } else { NA }; if (!is.na(cran_binary_url)) { pak::repo_add(CRAN = cran_binary_url) }; pak::pkg_install('renv'); if (!is.na(cran_binary_url)) { lf <- renv::lockfile_modify(repos = c('CRAN' = cran_binary_url)); tryCatch({ renv::lockfile_write(lf, './renv.lock') }, error = function(e) { invisible(NULL) }) }" """
            )
        else:
            dock = dock + "\nRUN R -e \"pak::pkg_install('renv')\""
        dock = dock + """RUN R -e "renv::restore()" """
    if detect_python:
        dock = dock + """
RUN test -f pyproject.toml || uv init --app . || true
RUN uv sync --all-groups --all-extras
RUN uv add -r requirements-tugboat.txt"""
    return dock


def create(
    project: str | Path = Path("."),
    FROM: str | None = "rocker/r-ver:latest",
    exclude: List[str] | str | None = None,
    verbose: bool = False,
    detect_r: bool = True,
    detect_python: bool = True,
    pigar_kwargs: Dict = {},
    renv_kwargs: Dict = {},
    optimize_pak: bool = True,
) -> None:
    """
    Generate a Dockerfile and .dockerignore from an analysis directory.

    Scans ``project`` for Python and/or R dependencies, writes a
    ``requirements.txt`` (Python) and/or ``renv.lock`` (R), and
    generates a Dockerfile that copies the project into the image and installs
    all detected dependencies. Python dependencies are installed with ``uv``;
    R dependencies are installed with ``pak`` and ``renv``.

    Parameters
    ----------
    project : str or Path, default current working directory
        Path to the analysis directory to generate a Dockerfile from.
    FROM : str or None, default "rocker/r-ver:latest"
        Base Docker image for the generated ``FROM`` instruction. Pass
        ``None`` to auto-detect: R projects use
        ``posit/r-base:{r_version}-noble``; Python-only projects default to
        ``python:{py_version}-slim``.
    exclude : list of str, str, or None, default None
        File(s) or sub-directories to exclude from the Docker image via
        the generated ``.dockerignore``.
    verbose : bool, default False
        Whether to print the generated Dockerfile contents.
    detect_r : bool, default True
        Whether to detect R dependencies and prepare the Docker image
        accordingly. At least one of ``detect_r`` or ``detect_python``
        must be True.
    detect_python : bool, default True
        Whether to detect Python dependencies and prepare the Docker image
        accordingly. At least one of ``detect_r`` or ``detect_python``
        must be True.
    pigar_kwargs : dict, default {}
        Keyword arguments forwarded to pigar's ``generate`` function
        (e.g. ``{"dry_run": True, "index_url": "..."}``).
    renv_kwargs : dict, default {}
        Keyword arguments forwarded to ``tugboat:::init_renv()``, which
        passes them on to ``renv::dependencies()``.
    optimize_pak : bool, default True
        When True, rewrites ``renv.lock`` to point at a Posit Package
        Manager binary mirror before running ``renv::restore()``, which
        substantially speeds up R package installation. Set to False if
        you encounter R package installation errors as a first debugging
        step.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If both ``detect_r`` and ``detect_python`` are False.
    """
    project = Path(project).resolve()
    if detect_python:
        # Scan for dependencies and generate requirements.txt
        _generate(
            requirement_file=str(project / "requirements-tugboat.txt"),
            project_path=project,
            **pigar_kwargs,
        )
    if detect_r:
        # Scan for dependencies and generate renv.lock
        _r_lockfile_with_temp_libpath(project=project, **renv_kwargs)
    if not detect_python and not detect_r:
        raise ValueError("At least one of `detect_r` or `detect_python` must be True.")
    # Generate .dockerignore
    _dockerignore(project=str(project), exclude=exclude)
    # Generate Dockerfile
    dock = _dockerfile(
        detect_r=detect_r,
        detect_python=detect_python,
        project=str(project),
        FROM=FROM,
        optimize_pak=optimize_pak,
    )
    if verbose:
        print(dock)
    dockerfile_path = Path(project) / "Dockerfile"
    dockerfile_path.write_text(dock)
