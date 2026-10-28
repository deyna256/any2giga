"""Extract the latest prepared release notes from the changelog."""

import argparse
import re
from pathlib import Path

HEADING = re.compile(r"(?m)^## \[([^\]\r\n]+)\] - \d{4}-\d{2}-\d{2}[ \t]*$")


def release_notes(changelog: str, version: str) -> str:
    headings = list(HEADING.finditer(changelog))
    if not headings or headings[0].group(1) != version:
        raise ValueError(f"The latest changelog entry must be for {version}.")

    start = headings[0].start()
    end = headings[1].start() if len(headings) > 1 else len(changelog)
    body = changelog[headings[0].end() : end].strip()
    if not body or body == "No significant changes.":
        raise ValueError(f"The changelog entry for {version} has no release notes.")
    return changelog[start:end].strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    args = parser.parse_args()
    try:
        print(release_notes(Path("CHANGELOG.md").read_text(encoding="utf-8"), args.version), end="")
    except ValueError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
