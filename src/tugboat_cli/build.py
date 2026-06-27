from pathlib import Path
import tugboat
from typing import List

def build(
    dockerfile: str | Path = Path(".") / "Dockerfile",
    image_name: str = "tugboat",
    tag: str = "latest",
    platforms: List[str] | str = ["linux/amd64", "linux/arm64"],
    build_args: List[str] | None = None,
    build_context: str = str(Path(".").resolve()),
    push: bool = False,
    dh_username: str | None = None,
    dh_password: str | None = None,
    verbose: bool = False,
) -> str:
    """
    Build a Docker image from a Dockerfile.

    Parameters
    ----------
    dockerfile : str or Path, default Path(".") / "Dockerfile"
        Path to the Dockerfile to build.
    image_name : str, default "tugboat"
        Name to assign to the built Docker image.
    tag : str, default "latest"
        Tag to assign to the built Docker image.
    platforms : list of str or str, default ["linux/amd64", "linux/arm64"]
        One or more target platforms to build the image for.
    build_args : list of str or None, default None
        Additional arguments to pass through to ``docker buildx build``.
    build_context : str, default current working directory
        Path to the build context directory.
    push : bool, default False
        Whether to push the built image to DockerHub. If True, both
        `dh_username` and `dh_password` must be provided.
    dh_username : str or None, default None
        DockerHub username. Required if `push` is True.
    dh_password : str or None, default None
        DockerHub password. Required if `push` is True.
    verbose : bool, default False
        Whether to print the underlying ``docker buildx build`` command
        before executing it.

    Returns
    -------
    str
        The full image reference, in the form ``{repository}:{tag}``.

    Raises
    ------
    DockerNotFoundError
        If Docker is not installed.
    RuntimeError
        If `push` is True but `dh_username` or `dh_password` is missing,
        if the Docker login fails, or if the build fails.
    """
    return tugboat.build(
        dockerfile=dockerfile,
        image_name=image_name,
        tag=tag,
        platforms=platforms,
        build_args=build_args,
        build_context=build_context,
        push=push,
        dh_username=dh_username,
        dh_password=dh_password,
        verbose=verbose
    )