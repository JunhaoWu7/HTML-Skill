#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def discover_skills() -> list[Path]:
    return sorted((REPO_ROOT / "skills").glob("*/SKILL.md"))


def parse_frontmatter(path: Path) -> tuple[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening YAML delimiter")
    try:
        closing_index = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("missing closing YAML delimiter") from error

    frontmatter = lines[1:closing_index]
    name = ""
    description = ""
    for index, line in enumerate(frontmatter):
        if line.startswith("name:"):
            name = line.partition(":")[2].strip().strip("'\"")
        if line.startswith("description:"):
            value = line.partition(":")[2].strip()
            if value in {">", ">-", "|", "|-"}:
                continuation = []
                for following in frontmatter[index + 1 :]:
                    if following and not following[0].isspace():
                        break
                    continuation.append(following.strip())
                description = " ".join(part for part in continuation if part)
            else:
                description = value.strip("'\"")
    return name, description


def main() -> int:
    skill_files = discover_skills()
    if not skill_files:
        print("ERROR: no Skills found; initialize submodules first", file=sys.stderr)
        return 1

    errors: list[str] = []
    seen_names: dict[str, Path] = {}
    for skill_file in skill_files:
        try:
            name, description = parse_frontmatter(skill_file)
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f"{skill_file}: {error}")
            continue

        if not NAME_PATTERN.fullmatch(name):
            errors.append(f"{skill_file}: invalid Skill name {name!r}")
        if name != skill_file.parent.name:
            errors.append(
                f"{skill_file}: name {name!r} must match folder {skill_file.parent.name!r}"
            )
        if not description:
            errors.append(f"{skill_file}: description is empty")
        if "TODO" in skill_file.read_text(encoding="utf-8"):
            errors.append(f"{skill_file}: unresolved TODO placeholder")
        if name in seen_names:
            errors.append(f"{skill_file}: duplicate Skill name also used by {seen_names[name]}")
        else:
            seen_names[name] = skill_file

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    for name in sorted(seen_names):
        print(f"VALID {name}: {seen_names[name].relative_to(REPO_ROOT)}")
    print(f"Validated {len(seen_names)} Skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
