"""Validate multilingual README badges against real pytest JUnit results.

This check is read-only, requires no GitHub tokens, and never changes main.
"""

import re
import sys
from pathlib import Path
from xml.etree import ElementTree

README_FILES = ("README.md", "README.pt-BR.md", "README.es.md")
EXPECTED_BADGE_COUNT = 30
PYTEST_BADGE = re.compile(
    r"!\[pytest\]\(https://img\.shields\.io/badge/pytest-(\d+)%20passing-0A9EDC\)"
)
IMAGE = re.compile(r"!\[[^\]]+\]\((https?://[^)]+)\)")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def junit_passed_count(report: Path) -> tuple[int, int, int]:
    """Return passed, skipped and failed/error totals from a pytest JUnit report."""
    root = ElementTree.parse(report).getroot()
    suite = root if root.tag == "testsuite" else root.find(".//testsuite")
    if suite is None:
        raise ValueError("JUnit XML contains no testsuite")
    tests = int(suite.attrib["tests"])
    skipped = int(suite.attrib.get("skipped", 0))
    failed = int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
    return tests - skipped - failed, skipped, failed


def validate(report: Path) -> None:
    passed, skipped, failed = junit_passed_count(report)
    if failed:
        raise ValueError(f"JUnit has {failed} failing/error tests")
    benchmark: list[str] | None = None
    section_count: int | None = None

    for file_name in README_FILES:
        path = Path(file_name)
        content = path.read_text(encoding="utf-8")
        if not content.startswith('<div align="center">'):
            raise ValueError(f"{file_name}: missing centered header")
        if "</div>" not in content:
            raise ValueError(f"{file_name}: unclosed centered header")
        header = content.split("</div>", 1)[0]
        images = IMAGE.findall(header)
        if len(images) != EXPECTED_BADGE_COUNT:
            raise ValueError(
                f"{file_name}: expected {EXPECTED_BADGE_COUNT} badges, got {len(images)}"
            )
        matches = PYTEST_BADGE.findall(header)
        if len(matches) != 1 or int(matches[0]) != passed:
            raise ValueError(
                f"{file_name}: pytest badge must show {passed} passed "
                f"({skipped} skipped; {failed} failed)"
            )
        if benchmark is None:
            benchmark = images
        elif images != benchmark:
            raise ValueError(f"{file_name}: badge URLs differ from README.md")
        sections = sum(line.startswith("## ") for line in content.splitlines())
        if section_count is None:
            section_count = sections
        elif sections != section_count:
            raise ValueError(f"{file_name}: translated section count differs")
        for link in MARKDOWN_LINK.findall(content):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local = link.split("#", 1)[0]
            if local and not (path.parent / local).exists():
                raise ValueError(f"{file_name}: missing link target {local}")
        for language in README_FILES:
            if f"]({language})" not in header:
                raise ValueError(f"{file_name}: missing link to {language}")
    print(
        f"README badges verified: {len(README_FILES)} languages, "
        f"{EXPECTED_BADGE_COUNT} badges each, {passed} pytest passing, "
        f"{skipped} skipped, {failed} failed"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: check_readme_badges.py pytest-report.xml")
    validate(Path(sys.argv[1]))
