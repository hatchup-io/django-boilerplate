#!/usr/bin/env python3
"""
Project initiation script for the GitHub template.

Run once after creating a new repository from this template to configure
the project name, slug, and package name across the codebase.

Usage:
    python scripts/init_project.py
    python scripts/init_project.py "My Project Name"
    python scripts/init_project.py "My Project" --slug myproject --package myproject-backend
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Project root (parent of scripts/)
ROOT = Path(__file__).resolve().parent.parent


def slugify(name: str) -> str:
    """Convert display name to a slug: lowercase, spaces and punctuation to hyphens."""
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s.strip("-") or "project"


def derive_package_name(slug: str) -> str:
    """Default package name for pyproject.toml (e.g. my-api-backend)."""
    return f"{slug}-backend" if not slug.endswith("-backend") else slug


def replace_in_file(file_path: Path, replacements: list[tuple[str, str]]) -> None:
    """Apply (old, new) string replacements in file. Uses exact match per line context."""
    if not file_path.exists():
        print(f"  Skip (not found): {file_path}")
        return
    text = file_path.read_text(encoding="utf-8")
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
    file_path.write_text(text, encoding="utf-8")
    print(f"  Updated: {file_path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Configure the project with a new name (run once after using the template)."
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        default=None,
        help="Display name for the project (e.g. 'Acme API').",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help="Project slug for containers, DB, cache (e.g. acme-api). Default: derived from project name.",
    )
    parser.add_argument(
        "--package",
        default=None,
        help="Python package name for pyproject.toml (e.g. acme-api-backend). Default: <slug>-backend.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be replaced without writing files.",
    )
    args = parser.parse_args()

    if args.project_name:
        project_name = args.project_name.strip()
    else:
        project_name = input("Project display name (e.g. Acme API): ").strip()
        if not project_name:
            print("Project name is required.")
            return 1

    slug = (args.slug or slugify(project_name)).strip().lower().replace(" ", "-")
    if not slug:
        slug = "project"
    package_name = (args.package or derive_package_name(slug)).strip()

    config = {
        "project_name": project_name,
        "project_slug": slug,
        "package_name": package_name,
    }

    if args.dry_run:
        print("Dry run. Would set:")
        print(json.dumps(config, indent=2))
        print(
            "Would copy .env.example to .env (if .env missing) and run poetry install."
        )
        return 0

    print(f"Configuring project: {project_name}")
    print(f"  slug: {slug}")
    print(f"  package: {package_name}")

    # File-specific replacements (order matters for overlapping strings)
    files_and_replacements: list[tuple[Path, list[tuple[str, str]]]] = [
        # pyproject.toml
        (
            ROOT / "pyproject.toml",
            [('name = "hatchup-backend"', f'name = "{package_name}"')],
        ),
        # docker-compose.yml
        (
            ROOT / "docker-compose.yml",
            [
                ("container_name: hatchup-db", f"container_name: {slug}-db"),
                ("container_name: hatchup-redis", f"container_name: {slug}-redis"),
                ("container_name: hatchup-rustfs", f"container_name: {slug}-rustfs"),
                ("container_name: hatchup-web", f"container_name: {slug}-web"),
                ("${DB_NAME:-hatchup}", "${DB_NAME:-" + slug + "}"),
                ("${RUSTFS_BUCKET_NAME:-hatchup}", "${RUSTFS_BUCKET_NAME:-" + slug + "}"),
            ],
        ),
        # core/settings.py
        (
            ROOT / "core/settings.py",
            [
                ('"KEY_PREFIX": "hatchup"', f'"KEY_PREFIX": "{slug}"'),
                ('"LOCATION": "hatchup-auth"', f'"LOCATION": "{slug}-auth"'),
            ],
        ),
        # core/packages/drf_spectacular.py (API title)
        (
            ROOT / "core/packages/drf_spectacular.py",
            [('"TITLE": "Boilerplate API"', f'"TITLE": "{project_name} API"')],
        ),
        # common/admins/base.py (admin site branding)
        (
            ROOT / "common/admins/base.py",
            [
                (
                    'site_header = "Hatchup Admin"',
                    f'site_header = "{project_name} Admin"',
                ),
                (
                    'site_title = "Hatchup Admin Portal"',
                    f'site_title = "{project_name} Admin Portal"',
                ),
                (
                    'index_title = "Welcome to Hatchup"',
                    f'index_title = "Welcome to {project_name}"',
                ),
                ('name="hatchup_admin"', f'name="{slug}_admin"'),
            ],
        ),
    ]

    for file_path, replacements in files_and_replacements:
        replace_in_file(file_path, replacements)

    # Write config for future reference / re-run
    config_path = ROOT / "project_config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"  Wrote: {config_path.relative_to(ROOT)}")

    # Copy .env.example to .env if .env does not exist
    env_example = ROOT / ".env.example"
    env_file = ROOT / ".env"
    if env_example.exists():
        if not env_file.exists():
            shutil.copy(env_example, env_file)
            print(f"  Copied: .env.example -> .env")
        else:
            print("  .env already exists; skipped copying .env.example")
    else:
        print("  Skip: .env.example not found")

    # Run uv sync
    print("\nRunning: uv sync")
    result = subprocess.run(
        ["uv", "sync"],
        cwd=ROOT,
        capture_output=False,
    )
    if result.returncode != 0:
        print("  uv sync failed; run it manually: uv sync")
        return result.returncode

    print("\nDone. Next step: python manage.py migrate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
