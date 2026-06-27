"""
tugboat-cli: high-level Python API for containerizing data science projects.

Provides three public functions:

- :func:`create` — scan a project directory for Python and/or R dependencies,
  then write a ``Dockerfile`` and ``.dockerignore``.
- :func:`build` — build (and optionally push) a Docker image from a Dockerfile
  using ``docker buildx``.
- :func:`binderize` — prepare a GitHub repository for launch via MyBinder by
  writing a ``.binder/Dockerfile`` and inserting a badge into the README.
"""

from .build import build
from .create import create
from .binderize import binderize

# read version from installed package
from importlib.metadata import version

__version__ = version("tugboat-cli")
