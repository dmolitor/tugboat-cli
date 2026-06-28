import click
from pathlib import Path

from .binderize import binderize as _binderize
from .build import build as _build
from .create import create as _create

_DEFAULT_PLATFORMS = ("linux/amd64", "linux/arm64")


@click.group()
@click.version_option(message="%(version)s")
def main():
    """Containerize R and Python projects with minimal configuration."""


@main.command("create")
@click.argument(
    "project",
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--from",
    "from_image",
    default="rocker/r-ver:latest",
    show_default=True,
    help=(
        "Base image for the Docker image. "
        "Pass an empty string to auto-detect: R projects use "
        "posit/r-base:{version}-noble; Python projects use python:{version}-slim."
    ),
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    metavar="PATTERN",
    help="File or directory to add to .dockerignore. May be repeated.",
)
@click.option(
    "--detect-r/--no-detect-r",
    default=True,
    show_default=True,
    help="Detect and install R and all dependencies in the image.",
)
@click.option(
    "--detect-python/--no-detect-python",
    default=True,
    show_default=True,
    help="Detect and install Python and all dependencies in the image.",
)
@click.option(
    "--optimize-pak/--no-optimize-pak",
    default=True,
    show_default=True,
    help=(
        "Use Posit Package Manager to install R binary packages. "
        "Disable as a first step when debugging R install errors."
    ),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Print the generated Dockerfile before writing it.",
)
def create_cmd(
    project, from_image, exclude, detect_r, detect_python, optimize_pak, verbose
):
    """
    Identify all necessary software and dependencies for an R or Python project.
    Create a corresponding Docker image.
    """
    _create(
        project=project,
        FROM=from_image or None,
        exclude=list(exclude) or None,
        verbose=verbose,
        detect_r=detect_r,
        detect_python=detect_python,
        optimize_pak=optimize_pak,
    )


@main.command("build")
@click.option(
    "--dockerfile",
    "-d",
    default="Dockerfile",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the Dockerfile.",
)
@click.option(
    "--image-name",
    "-n",
    default="tugboat",
    show_default=True,
    help="Name to assign to the built Docker image.",
)
@click.option(
    "--tag",
    "-t",
    default="latest",
    show_default=True,
    help="Tag to assign to the built Docker image.",
)
@click.option(
    "--platform",
    "-p",
    "platforms",
    multiple=True,
    metavar="PLATFORM",
    help=(
        f"Target platform (default: {', '.join(_DEFAULT_PLATFORMS)}). "
        "May be repeated to build for multiple platforms."
    ),
)
@click.option(
    "--build-arg",
    "build_args",
    multiple=True,
    metavar="ARG",
    help="Extra argument forwarded verbatim to docker buildx build. May be repeated.",
)
@click.option(
    "--build-context",
    default=None,
    type=click.Path(exists=True, file_okay=False),
    help="Build context directory. Defaults to the current working directory.",
)
@click.option(
    "--push",
    is_flag=True,
    default=False,
    help="Push the built image to DockerHub after building.",
)
@click.option(
    "--dh-username",
    default=None,
    envvar="DOCKERHUB_USERNAME",
    help="DockerHub username. Required when --push is set. Also reads from DOCKERHUB_USERNAME.",
)
@click.option(
    "--dh-password",
    default=None,
    hide_input=True,
    envvar="DOCKERUB_PASSWORD",
    help="DockerHub password. Required when --push is set. Also reads from DOCKERHUB_PASSWORD.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Print the docker buildx build command before executing it.",
)
def build_cmd(
    dockerfile,
    image_name,
    tag,
    platforms,
    build_args,
    build_context,
    push,
    dh_username,
    dh_password,
    verbose,
):
    """
    Build a Docker image from a Dockerfile and (optionally) upload
    the image to DockerHub.
    """
    _build(
        dockerfile=dockerfile,
        image_name=image_name,
        tag=tag,
        platforms=list(platforms) if platforms else list(_DEFAULT_PLATFORMS),
        build_args=list(build_args) or None,
        build_context=build_context or Path("."),
        push=push,
        dh_username=dh_username,
        dh_password=dh_password,
        verbose=verbose,
    )


@main.command("binderize")
@click.argument(
    "project",
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--detect-r/--no-detect-r",
    default=True,
    show_default=True,
    help="Detect and install R and all dependencies in the image.",
)
@click.option(
    "--detect-python/--no-detect-python",
    default=True,
    show_default=True,
    help="Detect and install Python and all dependencies in the image.",
)
@click.option(
    "--branch",
    "-b",
    default="main",
    show_default=True,
    help="Repository branch to point the Binder launch URL at.",
)
@click.option(
    "--urlpath",
    "-u",
    default="rstudio",
    show_default=True,
    help="URL path Binder opens on launch.",
)
@click.option(
    "--add-readme-badge/--no-add-readme-badge",
    default=True,
    show_default=True,
    help="Insert the Binder launch badge into README.md. When disabled, the badge snippet is copied to the clipboard instead.",
)
@click.option(
    "--overwrite/--no-overwrite",
    default=True,
    show_default=True,
    help="Whether to overwrite an existing .binder/Dockerfile.",
)
@click.option(
    "--optimize-pak/--no-optimize-pak",
    default=True,
    show_default=True,
    help=(
        "Use Posit Package Manager to install R binary packages. "
        "Disable as a first step when debugging R install errors."
    ),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Print the generated Binder Dockerfile before writing it.",
)
def binderize_cmd(
    project,
    detect_r,
    detect_python,
    branch,
    urlpath,
    add_readme_badge,
    overwrite,
    optimize_pak,
    verbose,
):
    """Prepare a GitHub repository for sharing via Binder."""
    _binderize(
        project=project,
        detect_r=detect_r,
        detect_python=detect_python,
        branch=branch,
        urlpath=urlpath,
        add_readme_badge=add_readme_badge,
        overwrite=overwrite,
        verbose=verbose,
        optimize_pak=optimize_pak,
    )
