#!/usr/bin/env python3
"""Utility helpers used by the README star update script.

This module intentionally keeps I/O and transformation logic separate from the
main orchestration flow so the top-level script stays easy to read.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Sequence
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

README_MARKDOWN_PATH = "README.md"
PROJECT_DATA_JSON_PATH = "data/projects.json"
TRACKED_README_SECTIONS = ("Plugins", "Integrations")
PLUGIN_CATEGORY_HEADINGS = (
    "Navigation",
    "Session Management",
    "Status Bar",
    "UI & Modes",
    "Search",
    "Utilities",
    "External Tools",
)

# We support both list-style entries and table-style entries while parsing,
# because older README content used bullets and newer content uses tables.
BULLET_ENTRY_REGEX = re.compile(r"^\* \[(.+?)\]\((.+?)\)\s*(.*)$")
TABLE_ENTRY_REGEX = re.compile(
    r"^\|\s*\[(.+?)\]\((.+?)\)\s*\|\s*([^|]*?)\s*\|\s*(.*?)\s*\|\s*$"
)


class RepoNotFoundError(RuntimeError):
    """Raised when GitHub confirms that a repository does not exist."""


def build_project_entry_record(
    entry_name: str,
    entry_url: str,
    entry_description: str,
    star_count: int | None,
) -> dict[str, Any]:
    """Create a normalized project entry record used by README parsing logic."""
    return {
        "name": entry_name,
        "url": entry_url,
        "description": entry_description.strip(),
        "stars": star_count,
    }


def fetch_github_stargazer_count(repository_owner: str, repository_name: str) -> int:
    """Fetch stargazer count from GitHub's repository API endpoint.

    A `RepoNotFoundError` is raised for HTTP 404 so callers can decide whether
    to fail fast (for stale links) instead of silently preserving old star data.
    """
    api_url = f"https://api.github.com/repos/{repository_owner}/{repository_name}"
    request_headers = {"User-Agent": "awesome-zellij-star-updater"}

    # Use an auth token when available to reduce the risk of rate limiting.
    github_api_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if github_api_token:
        request_headers["Authorization"] = f"Bearer {github_api_token}"

    request = Request(api_url, headers=request_headers)
    try:
        with urlopen(request, timeout=20) as response:
            response_payload = json.load(response)
    except HTTPError as request_error:
        if request_error.code == 404:
            missing_repository = f"{repository_owner}/{repository_name}"
            raise RepoNotFoundError(missing_repository) from request_error
        raise

    return int(response_payload.get("stargazers_count", 0))


def get_github_repository_identifier_from_url(
    project_url: str,
) -> tuple[str, str] | None:
    """Return `(owner, repo)` when a URL points to GitHub, otherwise `None`."""
    parsed_url = urlparse(project_url)
    if parsed_url.netloc.lower() != "github.com":
        return None

    path_segments = parsed_url.path.strip("/").split("/")
    if len(path_segments) < 2:
        return None

    repository_owner = path_segments[0]
    repository_name = path_segments[1].removesuffix(".git")
    return repository_owner, repository_name


def parse_project_entries_from_readme_lines(
    readme_lines: list[str],
    tracked_section_titles: Sequence[str],
) -> dict[str, list[dict[str, Any]]]:
    """Extract project entries for configured sections from README markdown."""
    parsed_entries_by_section: dict[str, list[dict[str, Any]]] = {}
    active_section_title: str | None = None

    for readme_line in readme_lines:
        if readme_line.startswith("# "):
            active_section_title = readme_line[2:].strip()
            if active_section_title in tracked_section_titles:
                parsed_entries_by_section.setdefault(active_section_title, [])
            continue

        if active_section_title not in tracked_section_titles:
            continue

        bullet_match = BULLET_ENTRY_REGEX.match(readme_line)
        if bullet_match:
            entry_name, entry_url, entry_description = bullet_match.groups()
            parsed_entries_by_section[active_section_title].append(
                build_project_entry_record(
                    entry_name,
                    entry_url,
                    entry_description,
                    None,
                )
            )
            continue

        table_match = TABLE_ENTRY_REGEX.match(readme_line)
        if not table_match:
            continue

        entry_name, entry_url, table_stars_text, entry_description = table_match.groups()
        parsed_star_value: int | None = None
        normalized_star_text = table_stars_text.strip()

        if normalized_star_text and normalized_star_text.upper() != "N/A":
            try:
                parsed_star_value = int(normalized_star_text.replace(",", ""))
            except ValueError:
                parsed_star_value = None

        parsed_entries_by_section[active_section_title].append(
            build_project_entry_record(
                entry_name,
                entry_url,
                entry_description,
                parsed_star_value,
            )
        )

    return parsed_entries_by_section


def write_json_document_to_file(json_document: dict[str, Any], json_file_path: str) -> None:
    """Write JSON with stable formatting and ensure parent directory exists."""
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    with open(json_file_path, "w", encoding="utf-8") as output_handle:
        json.dump(json_document, output_handle, indent=2, ensure_ascii=False)
        output_handle.write("\n")


def load_or_initialize_project_data(
    readme_lines: list[str],
    data_json_path: str,
    tracked_section_titles: Sequence[str],
) -> dict[str, Any]:
    """Load existing data JSON or bootstrap it from README content."""
    if os.path.exists(data_json_path):
        with open(data_json_path, "r", encoding="utf-8") as data_handle:
            return json.load(data_handle)

    parsed_entries_by_section = parse_project_entries_from_readme_lines(
        readme_lines,
        tracked_section_titles,
    )
    initialized_data_document = {
        "sections": [
            {
                "title": section_title,
                "items": parsed_entries_by_section.get(section_title, []),
            }
            for section_title in tracked_section_titles
        ]
    }

    write_json_document_to_file(initialized_data_document, data_json_path)
    return initialized_data_document


def sort_project_entries_by_name(project_entries: list[dict[str, Any]]) -> None:
    """Sort entries in-place by lowercase display name for deterministic output."""
    project_entries.sort(key=lambda project_entry: project_entry["name"].lower())


def format_stargazer_count_for_table(stargazer_count: int | None) -> str:
    """Format star values for markdown table output."""
    if stargazer_count is None:
        return "N/A"
    return f"{stargazer_count:,}"


def build_standard_project_markdown_table(
    project_entries: list[dict[str, Any]],
) -> list[str]:
    """Render one markdown table for a list of project entries."""
    markdown_lines = [
        "| Project | ⭐ | Description |",
        "| --- | --- | --- |",
    ]

    for project_entry in project_entries:
        # Escape `|` so descriptions do not break markdown table columns.
        escaped_description = project_entry["description"].replace("|", "\\|")
        markdown_lines.append(
            "| "
            f"[{project_entry['name']}]({project_entry['url']})"
            f" | {format_stargazer_count_for_table(project_entry.get('stars'))}"
            f" | {escaped_description} |"
        )

    return markdown_lines


def build_categorized_plugin_markdown_tables(
    plugin_entries: list[dict[str, Any]],
    category_headings_in_display_order: Sequence[str],
) -> list[str]:
    """Render plugin tables grouped by category heading."""
    markdown_lines: list[str] = []

    for category_heading in category_headings_in_display_order:
        category_entries = [
            entry
            for entry in plugin_entries
            if entry.get("category") == category_heading
        ]
        if not category_entries:
            continue

        sort_project_entries_by_name(category_entries)
        markdown_lines.append(f"## {category_heading}")
        markdown_lines.append("")
        markdown_lines.extend(build_standard_project_markdown_table(category_entries))
        markdown_lines.append("")

    return markdown_lines


def find_top_level_section_line_range(
    readme_lines: list[str],
    section_title: str,
) -> tuple[int, int] | None:
    """Find [start, end) line indexes for a top-level section heading."""
    section_start_line_index: int | None = None

    for line_index, readme_line in enumerate(readme_lines):
        if readme_line.startswith("# ") and readme_line[2:].strip() == section_title:
            section_start_line_index = line_index
            break

    if section_start_line_index is None:
        return None

    section_end_line_index = len(readme_lines)
    for line_index in range(section_start_line_index + 1, len(readme_lines)):
        if readme_lines[line_index].startswith("# "):
            section_end_line_index = line_index
            break

    return section_start_line_index, section_end_line_index


def replace_or_insert_last_updated_line(
    readme_lines: list[str],
    date_stamp_text: str,
) -> list[str]:
    """Set the README `Last updated:` line, adding it when missing."""
    last_updated_prefix = "Last updated:"

    for line_index, readme_line in enumerate(readme_lines):
        if readme_line.startswith(last_updated_prefix):
            readme_lines[line_index] = f"{last_updated_prefix} {date_stamp_text}"
            return readme_lines

    community_anchor_prefix = "All the resources listed are community-driven:"
    for line_index, readme_line in enumerate(readme_lines):
        if readme_line.startswith(community_anchor_prefix):
            insertion_line_index = line_index + 1
            readme_lines[insertion_line_index:insertion_line_index] = [
                "",
                f"{last_updated_prefix} {date_stamp_text}",
            ]
            return readme_lines

    # Fall back to inserting the timestamp at the top when no anchor exists.
    readme_lines.insert(0, f"{last_updated_prefix} {date_stamp_text}")
    readme_lines.insert(1, "")
    return readme_lines
