#!/usr/bin/env python3
"""Maintain project data and README tables for awesome-zellij.

This script exposes explicit flows:
- `sync`: refresh stars + render README + persist JSON
- `refresh-stars`: refresh stars in `data/projects.json` only
- `render`: render README from `data/projects.json` without API calls
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv

try:
    from rich.console import Console
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
    )
except ImportError:
    Console = None  # type: ignore[assignment]
    Progress = None  # type: ignore[assignment]

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


class CommandNames:
    """Named commands for the script CLI."""

    SYNC = "sync"
    REFRESH_STARS = "refresh-stars"
    RENDER = "render"


def print_progress_message(progress_message: str) -> None:
    """Print progress to stderr so users can see long-running activity."""
    print(f"[update_readme_stars] {progress_message}", file=sys.stderr)


def parse_command_line_arguments() -> argparse.Namespace:
    """Parse CLI args and require explicit command selection."""
    argument_parser = argparse.ArgumentParser(
        description=(
            "Maintain awesome-zellij project data and README tables. "
            "Choose an explicit flow command."
        )
    )

    command_subparsers = argument_parser.add_subparsers(
        dest="command_name",
        required=True,
    )

    command_subparsers.add_parser(
        CommandNames.SYNC,
        help="Refresh stars, then render README and write data/README.",
    )
    command_subparsers.add_parser(
        CommandNames.REFRESH_STARS,
        help="Refresh GitHub stars and write only data/projects.json.",
    )

    command_subparsers.add_parser(
        CommandNames.RENDER,
        help="Render README from data/projects.json with no network calls.",
    )

    return argument_parser.parse_args()


def should_use_rich_progress_bar() -> bool:
    """Enable rich progress only when it is available and output is interactive."""
    if Progress is None or Console is None:
        return False
    if not sys.stderr.isatty():
        return False
    if os.getenv("CI", "").strip().lower() in {"1", "true", "yes"}:
        return False
    return True


class RepositoryRefreshProgressTracker:
    """Show per-repository progress with rich when available, else plain logs."""

    def __init__(self, total_repository_count: int) -> None:
        self.total_repository_count = total_repository_count
        self.completed_repository_count = 0
        self.use_rich_progress_bar = (
            total_repository_count > 0 and should_use_rich_progress_bar()
        )
        self.rich_console: Any | None = None
        self.rich_progress: Any | None = None
        self.rich_task_identifier: Any | None = None

    def start(self) -> None:
        """Initialize the rich progress display if enabled."""
        if not self.use_rich_progress_bar:
            return

        self.rich_console = Console(stderr=True)
        self.rich_progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.rich_console,
            transient=False,
        )
        self.rich_progress.start()
        self.rich_task_identifier = self.rich_progress.add_task(
            "Fetching GitHub stars...",
            total=self.total_repository_count,
        )

    def record_repository_fetch(self, repository_owner: str, repository_name: str) -> None:
        """Advance progress for one repository fetch attempt."""
        self.completed_repository_count += 1
        repository_display_name = f"{repository_owner}/{repository_name}"

        if self.use_rich_progress_bar and self.rich_progress is not None:
            self.rich_progress.update(
                self.rich_task_identifier,
                advance=1,
                description=(
                    f"Fetching stars {self.completed_repository_count}/"
                    f"{self.total_repository_count}: {repository_display_name}"
                ),
            )
            return

        print_progress_message(
            "Fetching stars "
            f"{self.completed_repository_count}/{self.total_repository_count}: "
            f"{repository_display_name}"
        )

    def finish(self) -> None:
        """Close rich progress display and emit a final completion line."""
        if self.use_rich_progress_bar and self.rich_progress is not None:
            self.rich_progress.stop()

        print_progress_message(
            "Completed star refresh "
            f"for {self.completed_repository_count} GitHub repositories."
        )


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


def load_readme_lines_and_project_data() -> tuple[list[str], dict[str, Any]] | None:
    """Load README + data file and fail early if tracked sections are missing."""
    readme_lines = read_markdown_file_lines(README_MARKDOWN_PATH)
    tracked_sections_present_in_readme = collect_tracked_sections_present_in_readme(
        readme_lines
    )
    if not tracked_sections_present_in_readme:
        print("No matching sections found.", file=sys.stderr)
        return None

    project_data_document = load_or_initialize_project_data(
        readme_lines,
        PROJECT_DATA_JSON_PATH,
        TRACKED_README_SECTIONS,
    )
    return readme_lines, project_data_document


def iterate_tracked_sections_with_items(
    project_data_document: dict[str, Any],
):
    """Yield `(section_title, section_project_entries)` for tracked sections only."""
    for section_record in project_data_document.get("sections", []):
        section_title = section_record.get("title")
        if section_title not in TRACKED_README_SECTIONS:
            continue
        section_project_entries = section_record.get("items", [])
        yield section_title, section_project_entries


def count_github_repository_entries_in_tracked_sections(
    project_data_document: dict[str, Any],
) -> int:
    """Count GitHub-linked entries that will trigger API requests."""
    total_github_repository_entries = 0

    for _, section_project_entries in iterate_tracked_sections_with_items(
        project_data_document
    ):
        for project_entry in section_project_entries:
            project_url = project_entry.get("url", "")
            if get_github_repository_identifier_from_url(project_url):
                total_github_repository_entries += 1

    return total_github_repository_entries


def refresh_project_stars_and_collect_missing_repositories(
    project_data_document: dict[str, Any],
    total_github_repository_entries: int,
) -> list[dict[str, str]]:
    """Update star counts in-place and collect entries whose repos are gone.

    Behavior:
    - Missing GitHub repository (404): captured in the returned list.
    - Any other fetch issue: warning printed, existing stars preserved.
    """
    missing_repository_entries: list[dict[str, str]] = []
    progress_tracker = RepositoryRefreshProgressTracker(total_github_repository_entries)
    progress_tracker.start()

    try:
        for section_title, section_project_entries in iterate_tracked_sections_with_items(
            project_data_document
        ):
            if not section_project_entries:
                continue

            print_progress_message(
                f"Refreshing section '{section_title}' "
                f"({len(section_project_entries)} entries)."
            )

            for project_entry in section_project_entries:
                previous_stargazer_count = project_entry.get("stars")
                project_url = project_entry.get("url", "")
                repository_identifier = get_github_repository_identifier_from_url(project_url)

                # Only GitHub repositories expose stars in the way this script expects.
                if not repository_identifier:
                    project_entry["stars"] = previous_stargazer_count
                    continue

                repository_owner, repository_name = repository_identifier
                progress_tracker.record_repository_fetch(repository_owner, repository_name)
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
    finally:
        progress_tracker.finish()

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

    for section_title, section_project_entries in iterate_tracked_sections_with_items(
        project_data_document
    ):
        section_line_range = find_top_level_section_line_range(
            updated_readme_lines,
            section_title,
        )
        if not section_line_range:
            continue
        section_start_line_index, section_end_line_index = section_line_range

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


def refresh_stars_and_validate_repository_links(
    project_data_document: dict[str, Any],
) -> bool:
    """Refresh stars and return False after printing missing repo errors."""
    total_github_repository_entries = count_github_repository_entries_in_tracked_sections(
        project_data_document
    )
    print_progress_message(
        f"Found {total_github_repository_entries} GitHub repositories to refresh."
    )
    missing_repository_entries = refresh_project_stars_and_collect_missing_repositories(
        project_data_document,
        total_github_repository_entries,
    )
    if missing_repository_entries:
        print_missing_repository_report(missing_repository_entries)
        return False
    return True


def render_readme_and_write_to_disk(
    readme_lines: list[str],
    project_data_document: dict[str, Any],
) -> None:
    """Render README from project data and write it to disk."""
    updated_readme_lines = render_updated_readme_lines(readme_lines, project_data_document)
    write_markdown_file_lines(README_MARKDOWN_PATH, updated_readme_lines)


def run_refresh_stars_command() -> int:
    """Refresh stars only and persist `data/projects.json`."""
    print_progress_message("Starting flow: refresh-stars")
    print_progress_message("Stage 1/2: loading README and project data.")
    loaded_input = load_readme_lines_and_project_data()
    if loaded_input is None:
        return 1

    _, project_data_document = loaded_input

    print_progress_message("Stage 2/2: refreshing stars and writing project data.")
    if not refresh_stars_and_validate_repository_links(project_data_document):
        return 1

    write_json_document_to_file(project_data_document, PROJECT_DATA_JSON_PATH)
    print_progress_message("refresh-stars completed successfully.")
    return 0


def run_render_command() -> int:
    """Render README from project data and update timestamp."""
    print_progress_message("Starting flow: render")
    print_progress_message("Stage 1/2: loading README and project data.")
    loaded_input = load_readme_lines_and_project_data()
    if loaded_input is None:
        return 1

    readme_lines, project_data_document = loaded_input

    print_progress_message("Stage 2/2: rendering README from project data.")
    render_readme_and_write_to_disk(readme_lines, project_data_document)
    print_progress_message("render completed successfully.")
    return 0


def run_sync_command() -> int:
    """Refresh stars, then render README and persist both data and README."""
    print_progress_message("Starting flow: sync")

    print_progress_message("Stage 1/4: loading README and project data.")
    loaded_input = load_readme_lines_and_project_data()
    if loaded_input is None:
        return 1
    readme_lines, project_data_document = loaded_input

    print_progress_message("Stage 2/4: refreshing stars from GitHub.")
    stars_were_refreshed_successfully = refresh_stars_and_validate_repository_links(
        project_data_document
    )

    print_progress_message("Stage 3/4: validating repository health.")
    if not stars_were_refreshed_successfully:
        return 1

    print_progress_message("Stage 4/4: rendering README and writing output files.")
    render_readme_and_write_to_disk(readme_lines, project_data_document)
    write_json_document_to_file(project_data_document, PROJECT_DATA_JSON_PATH)
    print_progress_message("sync completed successfully.")
    return 0


def main() -> int:
    """Dispatch to one explicit maintenance flow."""
    load_dotenv()
    parsed_arguments = parse_command_line_arguments()

    if parsed_arguments.command_name == CommandNames.REFRESH_STARS:
        return run_refresh_stars_command()

    if parsed_arguments.command_name == CommandNames.RENDER:
        return run_render_command()

    if parsed_arguments.command_name == CommandNames.SYNC:
        return run_sync_command()

    print(
        f"Unknown command: {parsed_arguments.command_name}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
