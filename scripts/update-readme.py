#!/usr/bin/env python3
"""
Auto-update README.md with latest repos, activity, and timestamp.
Runs via GitHub Actions on schedule.
"""

import json
import os
import re
import urllib.request
from datetime import datetime, timezone

USERNAME = "ArapKBett"
README_PATH = "README.md"


def fetch_github_api(endpoint):
    """Fetch data from GitHub API."""
    url = f"https://api.github.com/{endpoint}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": USERNAME,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_latest_repos(limit=6):
    """Fetch latest updated repositories."""
    repos = fetch_github_api(
        f"users/{USERNAME}/repos?sort=updated&direction=desc&per_page={limit}&type=owner"
    )
    lines = []
    lines.append("```")
    lines.append(
        "╔══════════════════════════════════════════════════════════════════════════════╗"
    )
    lines.append(
        "║                     LATEST REPOSITORY DEPLOYMENTS                           ║"
    )
    lines.append(
        "╠══════════════════════════════════════════════════════════════════════════════╣"
    )

    for i, repo in enumerate(repos):
        name = repo["name"][:40]
        lang = repo.get("language") or "N/A"
        stars = repo.get("stargazers_count", 0)
        desc = (repo.get("description") or "No description")[:55]
        updated = repo["updated_at"][:10]

        lines.append("║                                                                            ║")
        lines.append(f"║  [{i+1:03d}] {name:<40}                         ║")
        lines.append(f"║  ├─ Lang:    {lang:<15} Stars: {stars:<5}                            ║")
        lines.append(f"║  ├─ Desc:    {desc:<55}  ║")
        lines.append(f"║  └─ Updated: {updated}                                                   ║")

    lines.append("║                                                                            ║")
    lines.append(
        "╚══════════════════════════════════════════════════════════════════════════════╝"
    )
    lines.append("```")
    return "\n".join(lines)


def get_recent_activity(limit=10):
    """Fetch recent public activity."""
    events = fetch_github_api(f"users/{USERNAME}/events/public?per_page=30")
    lines = []
    lines.append("```")
    lines.append(
        "┌──────────────────────────────────────────────────────────────────────────────┐"
    )
    lines.append(
        "│  [SYSLOG] Recent Operations                                                  │"
    )
    lines.append(
        "├──────────────────────────────────────────────────────────────────────────────┤"
    )

    count = 0
    for event in events:
        if count >= limit:
            break
        repo = event["repo"]["name"].replace(f"{USERNAME}/", "")
        event_type = event["type"]
        created = event["created_at"][:10]
        time_str = event["created_at"][11:16]

        icon = "●"
        action = ""

        if event_type == "PushEvent":
            commits = event["payload"].get("commits", [])
            n = len(commits)
            action = f"Pushed {n} commit{'s' if n != 1 else ''} to {repo}"
            icon = "⚡"
        elif event_type == "CreateEvent":
            ref_type = event["payload"].get("ref_type", "repository")
            action = f"Created {ref_type} in {repo}"
            icon = "✦"
        elif event_type == "DeleteEvent":
            ref_type = event["payload"].get("ref_type", "branch")
            action = f"Deleted {ref_type} in {repo}"
            icon = "✗"
        elif event_type == "WatchEvent":
            action = f"Starred {repo}"
            icon = "★"
        elif event_type == "ForkEvent":
            action = f"Forked {repo}"
            icon = "⑂"
        elif event_type == "IssuesEvent":
            act = event["payload"].get("action", "opened")
            action = f"{act.capitalize()} issue in {repo}"
            icon = "⚐"
        elif event_type == "PullRequestEvent":
            act = event["payload"].get("action", "opened")
            action = f"{act.capitalize()} PR in {repo}"
            icon = "⇌"
        elif event_type == "IssueCommentEvent":
            action = f"Commented on issue in {repo}"
            icon = "▶"
        elif event_type == "ReleaseEvent":
            action = f"Published release in {repo}"
            icon = "◆"
        else:
            action = f"{event_type.replace('Event', '')} in {repo}"

        action = action[:60]
        lines.append(
            f"│  {icon} [{created} {time_str}] {action:<60}│"
        )
        count += 1

    if count == 0:
        lines.append("│  No recent activity detected.                                                │")

    lines.append(
        "└──────────────────────────────────────────────────────────────────────────────┘"
    )
    lines.append("```")
    return "\n".join(lines)


def get_timestamp():
    """Generate auto-update timestamp."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f'<sub>Last system sync: {now} | Auto-updated by GitHub Actions</sub>'


def update_section(content, start_marker, end_marker, new_content):
    """Replace content between markers."""
    pattern = re.compile(
        rf"({re.escape(start_marker)})\n.*?\n({re.escape(end_marker)})",
        re.DOTALL,
    )
    replacement = f"{start_marker}\n{new_content}\n{end_marker}"
    return pattern.sub(replacement, content)


def main():
    with open(README_PATH, "r") as f:
        content = f.read()

    print("[*] Fetching latest repositories...")
    repos_content = get_latest_repos()
    content = update_section(content, "<!-- REPOS-START -->", "<!-- REPOS-END -->", repos_content)

    print("[*] Fetching recent activity...")
    activity_content = get_recent_activity()
    content = update_section(content, "<!-- ACTIVITY-START -->", "<!-- ACTIVITY-END -->", activity_content)

    print("[*] Updating timestamp...")
    timestamp_content = get_timestamp()
    content = update_section(
        content, "<!-- LAST-UPDATED-START -->", "<!-- LAST-UPDATED-END -->", timestamp_content
    )

    with open(README_PATH, "w") as f:
        f.write(content)

    print("[+] README.md updated successfully.")


if __name__ == "__main__":
    main()
