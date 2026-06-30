from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from tugboat_cli.cli import main
from tugboat_cli.create import _dockerfile
from tugboat_cli.binderize import _binder_dockerfile
from tugboat_cli.utils import _to_r_literal

# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------


@pytest.fixture
def runner():
    return CliRunner()


def test_version(runner):
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == version("tugboat-cli")


def test_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "create" in result.output
    assert "build" in result.output
    assert "binderize" in result.output


@pytest.mark.parametrize("subcommand", ["create", "build", "binderize"])
def test_subcommand_help(runner, subcommand):
    result = runner.invoke(main, [subcommand, "--help"])
    assert result.exit_code == 0


def test_create_forwards_options(runner, tmp_path):
    with patch("tugboat_cli.cli._create") as mock_create:
        result = runner.invoke(
            main,
            [
                "create",
                str(tmp_path),
                "--no-detect-r",
                "--no-detect-python",
                "--no-optimize-pak",
                "--verbose",
                "--exclude",
                "data/",
                "--exclude",
                "*.csv",
            ],
        )
        # ValueError is raised by _create when both detect flags are False,
        # but we're mocking _create so the call itself should succeed.
        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["detect_r"] is False
        assert kwargs["detect_python"] is False
        assert kwargs["optimize_pak"] is False
        assert kwargs["verbose"] is True
        assert kwargs["exclude"] == ["data/", "*.csv"]


def test_build_forwards_options(runner):
    with patch("tugboat_cli.cli._build") as mock_build:
        runner.invoke(
            main,
            [
                "build",
                "--image-name",
                "myimage",
                "--tag",
                "v1",
                "--platform",
                "linux/amd64",
                "--platform",
                "linux/arm64",
                "--push",
            ],
        )
        mock_build.assert_called_once()
        kwargs = mock_build.call_args.kwargs
        assert kwargs["image_name"] == "myimage"
        assert kwargs["tag"] == "v1"
        assert kwargs["platforms"] == ["linux/amd64", "linux/arm64"]
        assert kwargs["push"] is True


# ---------------------------------------------------------------------------
# Dockerfile generation
# ---------------------------------------------------------------------------


def test_dockerfile_both(tmp_path):
    out = _dockerfile(detect_r=True, detect_python=True, project=str(tmp_path))
    assert "renv" in out
    assert "uv" in out


def test_dockerfile_r_only(tmp_path):
    out = _dockerfile(detect_r=True, detect_python=False, project=str(tmp_path))
    assert "renv" in out
    assert "uv" not in out


def test_dockerfile_python_only(tmp_path):
    out = _dockerfile(detect_r=False, detect_python=True, project=str(tmp_path))
    assert "uv" in out
    assert "renv" not in out


def test_dockerfile_custom_from(tmp_path):
    out = _dockerfile(
        detect_r=False,
        detect_python=True,
        project=str(tmp_path),
        FROM="python:3.12-slim",
    )
    assert out.startswith("FROM python:3.12-slim")


def test_binder_dockerfile_both():
    out = _binder_dockerfile(detect_r=True, detect_python=True)
    assert "renv" in out
    assert "uv" in out


def test_binder_dockerfile_r_only():
    out = _binder_dockerfile(detect_r=True, detect_python=False)
    assert "renv" in out
    assert "uv" not in out


def test_binder_dockerfile_python_only():
    out = _binder_dockerfile(detect_r=False, detect_python=True)
    assert "uv" in out
    assert "renv" not in out


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def test_create_raises_when_no_detection(tmp_path):
    from tugboat_cli.create import create

    with pytest.raises(ValueError, match="At least one"):
        create(project=tmp_path, detect_r=False, detect_python=False)


def test_binderize_raises_for_non_github(tmp_path):
    import subprocess
    from tugboat_cli.binderize import binderize

    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "remote",
            "add",
            "origin",
            "https://gitlab.com/user/repo.git",
        ],
        check=True,
        capture_output=True,
    )
    with pytest.raises(ValueError, match="GitHub"):
        binderize(project=tmp_path)


# ---------------------------------------------------------------------------
# _to_r_literal
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "NULL"),
        (True, "TRUE"),
        (False, "FALSE"),
        (42, "42"),
        (3.14, "3.14"),
        ("hello", '"hello"'),
        ('say "hi"', '"say \\"hi\\""'),
        ([1, 2, 3], "c(1, 2, 3)"),
        (["a", "b"], 'c("a", "b")'),
        ([], "c()"),
        ((1, 2), "c(1, 2)"),
        (Path("/tmp/foo"), '"/tmp/foo"'),
    ],
)
def test_to_r_literal(value, expected):
    assert _to_r_literal(value) == expected


def test_to_r_literal_type_error():
    with pytest.raises(TypeError):
        _to_r_literal({"key": "val"})
