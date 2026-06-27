from pathlib import Path
from pygit2 import Repository
import re
from tugboat.binderize import _use_badge, BADGE_URL, DEFAULT_IMAGE


def _binder_dockerfile(
    detect_r: bool = True, detect_python: bool = True, optimize_pak: bool = True
) -> str:
    """
    Generate a Binder-compatible Dockerfile string.
    """
    dock = f"""FROM {DEFAULT_IMAGE}""" + """
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --chown=${NB_USER} . /home/rstudio
WORKDIR /home/rstudio
USER root
RUN printf "RETICULATE_PYTHON_ENV=/home/rstudio/.venv\\nVIRTUAL_ENV=/home/rstudio/.venv\\n" >> /usr/local/lib/R/etc/Renviron.site
USER ${NB_USER}
RUN test -f pyproject.toml || uv init --app . || true
RUN uv sync --all-groups --all-extras
RUN uv add -r requirements-tugboat.txt"""

    dock = f"FROM {DEFAULT_IMAGE}"
    if detect_python:
        dock = dock + "\nCOPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/"
    if detect_r:
        dock = dock + "\nCOPY renv.lock renv.lock"
    dock = dock + """
COPY --chown=${NB_USER} . /home/rstudio
WORKDIR /home/rstudio
USER root
RUN printf "RETICULATE_PYTHON_ENV=/home/rstudio/.venv\\nVIRTUAL_ENV=/home/rstudio/.venv\\n" >> /usr/local/lib/R/etc/Renviron.site
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
    dock = dock + "\nUSER ${NB_USER}"
    if detect_python:
        dock = dock + """
RUN test -f pyproject.toml || uv init --app . || true
RUN uv sync --all-groups --all-extras
RUN uv add -r requirements-tugboat.txt"""
    return dock

    return dock


def binderize(
    project: Path | str = Path("."),
    detect_r: bool = True,
    detect_python: bool = True,
    branch: str = "main",
    urlpath: str = "rstudio",
    add_readme_badge: bool = True,
    overwrite: bool = True,
    verbose: bool = False,
    optimize_pak: bool = True,
) -> None:
    """
    Prepare a GitHub repository to be launched via Binder.

    Writes a ``.binder/Dockerfile`` and inserts a Binder launch badge into
    the project's README.md (or copies the badge snippet to the clipboard
    if the README has no badge section to insert into).

    Parameters
    ----------
    project : Path or str, default Path(".")
        Path to the local Git repository to binderize. Must be a GitHub repository.
    detect_r : bool, default True
        Whether to detect R dependencies and prepare the Docker image accordingly.
        One of (or both) `detect_r` or `detect_python` must be set to True.
    detect_python : bool, default True
        Whether to detect Python dependencies and prepare the Docker image accordingly.
        One of (or both) `detect_r` or `detect_python` must be set to True.
    branch : str, default "main"
        Branch to point the Binder launch link at.
    urlpath : str, default "rstudio"
        URL path Binder should open to on launch (e.g. "rstudio", "lab").
    add_readme_badge : bool, default True
        Whether to attempt to insert the Binder badge into the project's
        README.md. If False, the badge snippet is copied to the clipboard
        and printed instead.
    overwrite : bool, default True
        Whether to overwrite an existing ``.binder/Dockerfile``.
    verbose : bool, default False
        Whether to print the generated Binder Dockerfile contents.
    optimize_pak : bool, default True
        Optimize R package installations in the Docker image. This should
        generally work. However, in some rare cases it can cause errors to
        occur. When encountering R package installation errors, setting this
        to False is typically a good, first debugging step.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If the repository is not a GitHub repository.
    """
    # Create repo object and extract url, username, repo name, etc.
    repo = Repository(project)
    git_remote = repo.remotes["origin"].url
    local_repo = Path(repo.workdir)
    username_repo = re.sub(r".*github\.com[:/](.*)\.git$", r"\1", git_remote).split("/")
    if git_remote.find("github.com") == -1:
        raise ValueError("Only GitHub repositories are currently supported.")
    # Generate Dockerfile
    dock = _binder_dockerfile(
        detect_r=detect_r, detect_python=detect_python, optimize_pak=optimize_pak
    )
    if verbose:
        print(dock)
    binder_dir = local_repo / ".binder"
    if not binder_dir.is_dir():
        binder_dir.mkdir()
    dockerfile_path = binder_dir / "Dockerfile"
    if overwrite or not dockerfile_path.exists():
        dockerfile_path.write_text(dock)
    # Construct Binder badge and insert into README (if possible)
    binder_url = f"https://mybinder.org/v2/gh/{'/'.join(username_repo)}/{branch}?urlpath={urlpath}"
    _use_badge(
        label="Launch RStudio Binder",
        href=binder_url,
        image_url=BADGE_URL,
        readme=local_repo / "README.md",
        add_readme_badge=add_readme_badge,
    )
    # Give the user final instructions
    print("Your repository has been configured for Binder.")
    print("[x] Commit and push all changes")
    print("[x] Launch Binder at: ", binder_url)
