#!/usr/bin/env python3
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from dotenv import load_dotenv

README_PATH = "README.md"
DATA_PATH = "data/projects.json"
SECTIONS = ["Plugins", "Integrations"]
PLUGIN_CATEGORIES = [
    "Navigation",
    "Session Management",
    "Status Bar",
    "UI & Modes",
    "Search",
    "Utilities",
    "External Tools",
]


def fetch_github_stars(owner: str, repo: str) -> int:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"User-Agent": "awesome-zellij-star-updater"}
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    return int(data.get("stargazers_count", 0))


def parse_repo(url: str):
    parsed = urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    repo = repo.removesuffix(".git")
    return owner, repo


def parse_readme_sections(lines):
    sections = {}
    current = None
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            current = title
            if current in SECTIONS:
                sections.setdefault(current, [])
            continue
        if current not in SECTIONS:
            continue

        if line.startswith("*"):
            match = re.match(r"^\* \[(.+?)\]\((.+?)\)\s*(.*)$", line)
            if not match:
                continue
            name, url, desc = match.groups()
            sections[current].append(
                {
                    "name": name,
                    "url": url,
                    "description": desc.strip(),
                    "stars": None,
                }
            )
            continue

        if line.startswith("|") and "[" in line and "](" in line:
            match = re.match(
                r"^\|\s*\[(.+?)\]\((.+?)\)\s*\|\s*([^|]*?)\s*\|\s*(.*?)\s*\|\s*$",
                line,
            )
            if not match:
                continue
            name, url, stars_text, desc = match.groups()
            stars_text = stars_text.strip()
            stars = None
            if stars_text and stars_text.upper() != "N/A":
                try:
                    stars = int(stars_text.replace(",", ""))
                except ValueError:
                    stars = None
            sections[current].append(
                {
                    "name": name,
                    "url": url,
                    "description": desc.strip(),
                    "stars": stars,
                }
            )
    return sections


def load_data(lines):
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)

    sections = parse_readme_sections(lines)
    data = {
        "sections": [
            {"title": title, "items": sections.get(title, [])}
            for title in SECTIONS
        ]
    }
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return data


def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def format_stars(stars):
    if stars is None:
        return "N/A"
    return f"{stars:,}"


def build_table(items):
    lines = [
        "| Project | Stars ⭐ | Description |",
        "| --- | --- | --- |",
    ]
    for item in items:
        desc = item["description"].replace("|", "\\|")
        lines.append(
            f"| [{item['name']}]({item['url']}) | {format_stars(item['stars'])} | {desc} |"
        )
    return lines


def build_categorized_tables(items):
    """Build tables grouped by category with alphabetical sorting."""
    lines = []
    for category in PLUGIN_CATEGORIES:
        cat_items = [i for i in items if i.get("category") == category]
        if not cat_items:
            continue
        cat_items.sort(key=lambda x: x["name"].lower())
        lines.append(f"## {category}")
        lines.append("")
        lines.extend(build_table(cat_items))
        lines.append("")
    return lines


def update_timestamp(lines, timestamp):
    target = "Last updated:"
    for idx, line in enumerate(lines):
        if line.startswith(target):
            lines[idx] = f"{target} {timestamp}"
            return lines

    anchor = "All the resources listed are community-driven:"
    for idx, line in enumerate(lines):
        if line.startswith(anchor):
            insert_at = idx + 1
            lines[insert_at:insert_at] = ["", f"{target} {timestamp}"]
            return lines

    lines.insert(0, f"{target} {timestamp}")
    lines.insert(1, "")
    return lines


def main():
    load_dotenv()
    with open(README_PATH, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    def find_section_range(current_lines, title):
        start_idx = None
        for idx, line in enumerate(current_lines):
            if line.startswith("# ") and line[2:].strip() == title:
                start_idx = idx
                break
        if start_idx is None:
            return None
        end_idx = len(current_lines)
        for idx in range(start_idx + 1, len(current_lines)):
            if current_lines[idx].startswith("# "):
                end_idx = idx
                break
        return start_idx, end_idx

    found_sections = [
        section for section in SECTIONS if find_section_range(lines, section)
    ]
    if not found_sections:
        print("No matching sections found.", file=sys.stderr)
        return 1

    data = load_data(lines)
    new_lines = lines[:]

    for section in data.get("sections", []):
        title = section.get("title")
        if title not in SECTIONS:
            continue
        section_range = find_section_range(new_lines, title)
        if not section_range:
            continue
        start_idx, end_idx = section_range

        items = section.get("items", [])
        if not items:
            continue

        for item in items:
            existing_stars = item.get("stars")
            repo = parse_repo(item["url"])
            if not repo:
                item["stars"] = existing_stars
                continue
            owner, repo_name = repo
            try:
                item["stars"] = fetch_github_stars(owner, repo_name)
            except Exception as exc:
                print(
                    f"Failed to fetch stars for {owner}/{repo_name}: {exc}",
                    file=sys.stderr,
                )
                item["stars"] = existing_stars
            time.sleep(0.1)

        # Sort alphabetically
        items.sort(key=lambda x: x["name"].lower())

        # Use categorized tables for Plugins, regular table for Integrations
        if title == "Plugins":
            table_lines = build_categorized_tables(items)
        else:
            table_lines = build_table(items)
            table_lines.append("")  # Add trailing newline for non-categorized

        new_lines = (
            new_lines[: start_idx + 1]
            + [""]
            + table_lines
            + new_lines[end_idx:]
        )

    with open(README_PATH, "w", encoding="utf-8") as f:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_lines = update_timestamp(new_lines, timestamp)
        f.write("\n".join(new_lines) + "\n")
    save_data(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
