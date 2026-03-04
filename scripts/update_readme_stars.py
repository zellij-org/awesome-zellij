#!/usr/bin/env python3
"""Main flow for updating README project stars.

The orchestration in this file intentionally reads like a checklist:
1) load inputs, 2) refresh star data, 3) render markdown, 4) write outputs.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv

from update_readme_stars_utils import (
    PLUGIN_CATEGORY_HEADINGS,
    PROJECT_DATA_JSON_PATH,
    README_MARKDOWN_PATH,
    TRACKED_README_SECTIONS,
    RepoNotFoundError,
    build_categorized_plugin_markdown_tables,
    build_standard_project_markdown_table,
    fetch_github_stargazer_count,
    find_top_level_section_line_range,
    get_github_repository_identifier_from_url,
    load_or_initialize_project_data,
    replace_or_insert_last_updated_line,
    sort_project_entries_by_name,
    write_json_document_to_file,
)

# Keep a small pause between API calls to avoid hammering GitHub.
SECONDS_TO_WAIT_BETWEEN_GITHUB_REQUESTS = 0.1


def read_markdown_file_lines(markdown_file_path: str) -> list[str]:
    """Read markdown file content and return split lines without newline suffixes."""
    with open(markdown_file_path, "r", encoding="utf-8") as markdown_handle:
        return markdown_handle.read().splitlines()


def write_markdown_file_lines(markdown_file_path: str, markdown_lines: list[str]) -> None:
    """Write markdown lines back to disk with a trailing newline."""
    with open(markdown_file_path, "w", encoding="utf-8") as markdown_handle:
        markdown_handle.write("\n".join(markdown_lines) + "\n")


def collect_tracked_sections_present_in_readme(readme_lines: list[str]) -> list[str]:
    """Return tracked top-level sections that currently exist in README."""
    tracked_sections_present_in_readme: list[str] = []

    for tracked_section_title in TRACKED_README_SECTIONS:
        if find_top_level_section_line_range(readme_lines, tracked_section_title):
            tracked_sections_present_in_readme.append(tracked_section_title)

    return tracked_sections_present_in_readme


def refresh_project_stars_and_collect_missing_repositories(
    project_data_document: dict[str, Any],
) -> list[dict[str, str]]:
    """Update star counts in-place and collect entries whose repos are gone.

    Behavior:
    - Missing GitHub repository (404): captured in the returned list.
    - Any other fetch issue: warning printed, existing stars preserved.
    """
    missing_repository_entries: list[dict[str, str]] = []

    for section_record in project_data_document.get("sections", []):
        section_title = section_record.get("title")
        if section_title not in TRACKED_README_SECTIONS:
            continue

        section_project_entries = section_record.get("items", [])
        if not section_project_entries:
            continue

        for project_entry in section_project_entries:
            previous_stargazer_count = project_entry.get("stars")
            project_url = project_entry.get("url", "")
            repository_identifier = get_github_repository_identifier_from_url(project_url)

            # Only GitHub repositories expose stars in the way this script expects.
            if not repository_identifier:
                project_entry["stars"] = previous_stargazer_count
                continue

            repository_owner, repository_name = repository_identifier
            try:
                project_entry["stars"] = fetch_github_stargazer_count(
                    repository_owner,
                    repository_name,
                )
            except RepoNotFoundError:
                missing_repository_entries.append(
                    {
                        "section": str(section_title),
                        "name": str(project_entry.get("name", "Unknown project")),
                        "repo": f"{repository_owner}/{repository_name}",
                        "url": project_url,
                    }
                )
                project_entry["stars"] = previous_stargazer_count
            except Exception as unexpected_error:
                print(
                    "Failed to fetch stars for "
                    f"{repository_owner}/{repository_name}: {unexpected_error}",
                    file=sys.stderr,
                )
                project_entry["stars"] = previous_stargazer_count

            time.sleep(SECONDS_TO_WAIT_BETWEEN_GITHUB_REQUESTS)

    return missing_repository_entries


def print_missing_repository_report(missing_repository_entries: list[dict[str, str]]) -> None:
    """Print a clear action list for projects whose GitHub repositories are gone."""
    print(
        "One or more GitHub repositories were not found. "
        "Please update or remove these entries:",
        file=sys.stderr,
    )

    for missing_repository_entry in missing_repository_entries:
        print(
            f"- [{missing_repository_entry['section']}] "
            f"{missing_repository_entry['name']} "
            f"({missing_repository_entry['repo']}) -> "
            f"{missing_repository_entry['url']}",
            file=sys.stderr,
        )


def render_updated_readme_lines(
    original_readme_lines: list[str],
    project_data_document: dict[str, Any],
) -> list[str]:
    """Render tracked sections from project data and return full README lines."""
    updated_readme_lines = original_readme_lines[:]

    for section_record in project_data_document.get("sections", []):
        section_title = section_record.get("title")
        if section_title not in TRACKED_README_SECTIONS:
            continue

        section_line_range = find_top_level_section_line_range(
            updated_readme_lines,
            section_title,
        )
        if not section_line_range:
            continue
        section_start_line_index, section_end_line_index = section_line_range

        section_project_entries = section_record.get("items", [])
        if not section_project_entries:
            continue

        # Keep list output deterministic so diffs remain easy to review.
        sort_project_entries_by_name(section_project_entries)

        if section_title == "Plugins":
            rendered_section_lines = build_categorized_plugin_markdown_tables(
                section_project_entries,
                PLUGIN_CATEGORY_HEADINGS,
            )
        else:
            rendered_section_lines = build_standard_project_markdown_table(
                section_project_entries,
            )
            rendered_section_lines.append("")

        updated_readme_lines = (
            updated_readme_lines[: section_start_line_index + 1]
            + [""]
            + rendered_section_lines
            + updated_readme_lines[section_end_line_index:]
        )

    utc_date_stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return replace_or_insert_last_updated_line(updated_readme_lines, utc_date_stamp)


def main() -> int:
    """Execute the full README star-update flow."""
    load_dotenv()

    # Stage 1: Load source markdown and ensure required sections exist.
    readme_lines = read_markdown_file_lines(README_MARKDOWN_PATH)
    tracked_sections_present_in_readme = collect_tracked_sections_present_in_readme(
        readme_lines
    )
    if not tracked_sections_present_in_readme:
        print("No matching sections found.", file=sys.stderr)
        return 1

    # Stage 2: Load cached project data, then refresh stars from GitHub.
    project_data_document = load_or_initialize_project_data(
        readme_lines,
        PROJECT_DATA_JSON_PATH,
        TRACKED_README_SECTIONS,
    )
    missing_repository_entries = refresh_project_stars_and_collect_missing_repositories(
        project_data_document
    )

    # Stage 3: Stop early when links are stale, so maintainers can fix entries.
    if missing_repository_entries:
        print_missing_repository_report(missing_repository_entries)
        return 1

    # Stage 4: Render README sections and persist both README + JSON cache.
    updated_readme_lines = render_updated_readme_lines(readme_lines, project_data_document)
    write_markdown_file_lines(README_MARKDOWN_PATH, updated_readme_lines)
    write_json_document_to_file(project_data_document, PROJECT_DATA_JSON_PATH)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
