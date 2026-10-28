import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    shutil.copy2(ROOT / "Justfile", tmp_path / "Justfile")
    source = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ruff_lines = []
    collecting = False
    for line in source.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            collecting = stripped == "[tool.ruff]" or stripped.startswith("[tool.ruff.")
        if collecting:
            ruff_lines.append(line)
    assert ruff_lines
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "just-probe"\nversion = "0.1.0"\n'
        'requires-python = ">=3.12"\ndependencies = []\n\n' + "".join(ruff_lines),
        encoding="utf-8",
    )

    env = {
        name: value
        for name, value in os.environ.items()
        if not name.startswith("UV_") and name not in {"VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME"}
    }
    env.update(
        UV_CACHE_DIR=str(tmp_path / "cache"),
        UV_OFFLINE="1",
        UV_PYTHON_DOWNLOADS="never",
        UV_PYTHON=sys.executable,
        UV_PROJECT_ENVIRONMENT=str(tmp_path / ".venv"),
    )
    subprocess.run(
        ["uv", "lock", "--offline"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["uv", "venv", "--offline", "--python", sys.executable, str(tmp_path / ".venv")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    ruff = Path(sys.executable).parent / ("ruff.exe" if os.name == "nt" else "ruff")
    target = tmp_path / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ruff.name
    shutil.copy2(ruff, target)
    return tmp_path, env


def command(project: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=project, env=env, capture_output=True, text=True, timeout=30)


def test_format_then_lint_after_autofix(project: tuple[Path, dict[str, str]]) -> None:
    path, env = project
    env["UV_NO_SYNC"] = "1"
    (path / "probe.py").write_text(
        "from typing import Optional, List\n\n"
        "def f(v: Optional[List[int]]) -> Optional[List[str]]:\n"
        "    return [str(x) for x in v] if v is not None else None\n",
        encoding="utf-8",
    )
    result = command(path, env, "just", "format")
    assert result.returncode == 0, result.stdout + result.stderr
    result = command(path, env, "just", "lint")
    assert result.returncode == 0, result.stdout + result.stderr


def test_lint_rejects_stale_lock_without_writing_it(project: tuple[Path, dict[str, str]]) -> None:
    path, env = project
    pyproject = path / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    version = tomllib.loads(content)["project"]["version"]
    original = f'version = "{version}"'
    assert original in content
    pyproject.write_text(content.replace(original, 'version = "99.0.0"', 1), encoding="utf-8")

    lock = path / "uv.lock"
    before = lock.read_bytes()
    result = command(path, env, "just", "lint")
    assert result.returncode != 0, result.stdout + result.stderr
    assert "lockfile" in (result.stdout + result.stderr).lower()
    assert "--locked" in result.stdout + result.stderr
    assert lock.read_bytes() == before
