#!/usr/bin/env python3
"""
check_lost_links.py — catch links dropped by the stars-updater run.

Run this right after markdown-github-stars-updater has rewritten your
markdown file (before you commit). It compares the file's link set now
against one or more previous git-committed versions of the same file and
reports any link that has disappeared. Total link count is allowed (and
expected) to grow — it must never shrink without explanation.

USAGE
    # Compare working tree against the last commit (the normal case:
    # run this right after the stars-updater, before `git add`/commit)
    python3 check_lost_links.py README.md

    # Compare against an arbitrary point in history
    python3 check_lost_links.py README.md --against origin/main
    python3 check_lost_links.py README.md --against HEAD~5

    # Look further back: union the link sets from the last N commits of
    # the file, so a loss that slipped through an earlier update is still
    # caught (not just a regression from the very last commit)
    python3 check_lost_links.py README.md --history 10

    # Compare two arbitrary git revisions instead of "vs working tree"
    python3 check_lost_links.py README.md --old-ref HEAD~1 --new-ref HEAD

    # Permanently silence a link you removed on purpose (dead repo, dup, etc.)
    python3 check_lost_links.py README.md --allow .lost-links-allow

    # Machine-readable output for CI
    python3 check_lost_links.py README.md --json

EXIT CODE
    0  no links lost (count may have grown, that's fine)
    1  one or more links from a previous version are missing now
    2  usage / git error

SUGGESTED CI USAGE (after the stars-updater step, before commit/push):
    - run: python3 check_lost_links.py README.md --history 5
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from urllib.parse import urlsplit, urlunsplit

# Matches markdown inline links: [text](url)
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def git(*args: str, cwd: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout


def file_at_ref(path: str, ref: str) -> str:
    """Return the file's content as of a given git ref ('WORKTREE' = disk)."""
    if ref == "WORKTREE":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return git("show", f"{ref}:{path}")


def extract_links(text: str) -> dict[str, str]:
    """Return {url: link_text} for every markdown link found, in order."""
    links: dict[str, str] = {}
    for match in LINK_RE.finditer(text):
        link_text, url = match.group(1), match.group(2)
        links[url] = link_text
    return links


def normalize(url: str) -> str:
    """Loose form of a URL, used only to tell 'removed' from 'just edited'."""
    parts = urlsplit(url.strip())
    scheme = "https"  # http vs https shouldn't count as a different resource
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parts.path.rstrip("/")
    if path.endswith(".git"):
        path = path[: -len(".git")]
    return urlunsplit((scheme, netloc, path, "", ""))


def commits_touching(path: str, count: int) -> list[str]:
    """Last `count` commit hashes (newest first) that touched `path`."""
    out = git("log", f"-{count}", "--format=%H", "--", path)
    return [line for line in out.splitlines() if line]


def load_allowlist(path: str | None) -> set[str]:
    if not path:
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            }
    except FileNotFoundError:
        return set()


def build_baseline(path: str, ref: str | None, history: int) -> dict[str, str]:
    """Union of links found across the requested set of past versions."""
    baseline: dict[str, str] = {}
    if history and history > 1:
        refs = commits_touching(path, history)
        if not refs:
            raise RuntimeError(f"no commit history found for {path}")
        for r in refs:
            content = file_at_ref(path, r)
            for url, text in extract_links(content).items():
                baseline.setdefault(url, text)
    else:
        baseline_ref = ref or "HEAD"
        content = file_at_ref(path, baseline_ref)
        baseline = extract_links(content)
    return baseline


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect links dropped from a markdown awesome-list file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("file", help="path to the markdown file, e.g. README.md")
    parser.add_argument(
        "--against",
        metavar="REF",
        help="git ref to treat as the baseline (default: HEAD)",
    )
    parser.add_argument(
        "--history",
        type=int,
        default=1,
        metavar="N",
        help="union the link sets from the last N commits touching the file, "
        "instead of just one baseline ref (default: 1, i.e. just --against)",
    )
    parser.add_argument(
        "--old-ref",
        metavar="REF",
        help="compare two git refs instead of baseline-vs-working-tree",
    )
    parser.add_argument(
        "--new-ref",
        metavar="REF",
        help="new-side ref when using --old-ref (default: working tree on disk)",
    )
    parser.add_argument(
        "--allow",
        metavar="FILE",
        help="path to a file of one-URL-per-line entries to permanently ignore "
        "(intentionally removed links)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    try:
        if args.old_ref:
            old_links = extract_links(file_at_ref(args.file, args.old_ref))
        else:
            old_links = build_baseline(args.file, args.against, args.history)

        new_ref = args.new_ref or "WORKTREE"
        new_links = extract_links(file_at_ref(args.file, new_ref))
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    allowlist = load_allowlist(args.allow)

    old_norm = {normalize(u): u for u in old_links}
    new_norm = {normalize(u): u for u in new_links}

    missing_norm = set(old_norm) - set(new_norm) - {normalize(u) for u in allowlist}

    truly_removed = []  # gone, no trace even under loose matching
    edited = []  # present but URL changed slightly (proto/slash/.git/www)
    for n in sorted(missing_norm, key=lambda k: old_links[old_norm[k]] and old_norm[k]):
        url = old_norm[n]
        truly_removed.append((url, old_links[url]))

    old_count, new_count = len(old_links), len(new_links)

    report = {
        "file": args.file,
        "old_link_count": old_count,
        "new_link_count": new_count,
        "count_delta": new_count - old_count,
        "lost_links": [{"url": u, "text": t} for u, t in truly_removed],
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1 if truly_removed else 0

    print(f"{args.file}: {old_count} link(s) before -> {new_count} link(s) now "
          f"({report['count_delta']:+d})")

    if not truly_removed:
        print("OK: no links were lost.")
        return 0

    print(f"\n LOST {len(truly_removed)} link(s) that were present before "
          "and are missing now:\n")
    for url, text in truly_removed:
        label = text if text else "(no text)"
        print(f"  - {label}\n      {url}")

    print(
        "\nIf any of these were removed on purpose (dead repo, duplicate, "
        "curation decision), add them to your allowlist file so future runs "
        "stop flagging them, e.g.:\n"
        f"  echo '{truly_removed[0][0]}' >> .lost-links-allow"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
