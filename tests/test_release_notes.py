import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "release_notes.py"


def run_notes(tmp_path: Path, changelog: str, version: str) -> subprocess.CompletedProcess[str]:
    (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), version],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )


def test_extracts_only_the_latest_release(tmp_path: Path) -> None:
    result = run_notes(
        tmp_path,
        "# Changelog\n\n## [1.2.0] - 2026-01-01\n\n### Added\n- New feature.\n\n"
        "## [1.1.0] - 2025-12-01\n\n- Old feature.\n",
        "1.2.0",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "## [1.2.0] - 2026-01-01\n\n### Added\n- New feature.\n"


@pytest.mark.parametrize(
    ("changelog", "version"),
    [
        ("# Changelog\n", "1.2.0"),
        ("## [1.3.0] - 2026-01-01\n\nNew.\n## [1.2.0] - 2025-12-01\n\nOld.\n", "1.2.0"),
        ("## [1.2.0] - 2026-01-01\n", "1.2.0"),
        ("## [1.2.0] - 2026-01-01\n\nNo significant changes.\n", "1.2.0"),
    ],
)
def test_rejects_missing_or_unprepared_release_notes(
    tmp_path: Path, changelog: str, version: str
) -> None:
    result = run_notes(tmp_path, changelog, version)
    assert result.returncode != 0
    assert not result.stdout
