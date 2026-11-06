"""git-insights: pull my GitHub commits into SQLite and chart them per week.

Usage:
    python3 git_insights.py fetch   # download repos + commits into git_insights.db
    python3 git_insights.py chart   # plot commits per week -> commits_per_week.png

Set GITHUB_TOKEN in your environment to raise the API rate limit
(60 requests/hour without a token, 5000 with one).
"""
import os
import sqlite3
import sys
from datetime import date, timedelta

import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

GITHUB_USER = "UsmanNYusuf"
API = "https://api.github.com"
DB_PATH = "git_insights.db"
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
CHART_PATH = "commits_per_week.png"


def make_session():
    session = requests.Session()
    session.headers["Accept"] = "application/vnd.github+json"
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    else:
        print("Warning: GITHUB_TOKEN not set, limited to 60 requests/hour.")
    return session


def get_paginated(session, url, params=None):
    """Return every item from a paginated GitHub endpoint by following Link headers.

    Returns an empty list for 409 Conflict (GitHub's response for an empty repo).
    """
    params = {"per_page": 100, **(params or {})}
    items = []
    while url:
        try:
            response = session.get(url, params=params)
            if response.status_code == 409:
                return []
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            sys.exit(1)
        items.extend(response.json())
        # The "next" URL already contains the query string, so drop params after page 1.
        url = response.links.get("next", {}).get("url")
        params = None
    return items


def fetch_repositories(session):
    return get_paginated(session, f"{API}/users/{GITHUB_USER}/repos")


def fetch_commits(session, repo_name):
    url = f"{API}/repos/{GITHUB_USER}/{repo_name}/commits"
    return get_paginated(session, url, params={"author": GITHUB_USER})


def initialize_database(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())


def save(conn, repo, commits):
    conn.execute(
        "INSERT OR IGNORE INTO repos (id, name) VALUES (?, ?)",
        (repo["id"], repo["name"]),
    )
    conn.executemany(
        """
        INSERT OR IGNORE INTO commits (sha, repo_id, author, date, message)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                commit["sha"],
                repo["id"],
                commit["commit"]["author"]["name"],
                commit["commit"]["author"]["date"],
                commit["commit"]["message"],
            )
            for commit in commits
        ],
    )
    conn.commit()


def commits_per_week(conn):
    # Group by the Monday each commit's week starts on:
    # 'weekday 0' moves forward to Sunday, then '-6 days' goes back to that week's Monday.
    return conn.execute(
        """
        SELECT date(date, 'weekday 0', '-6 days') AS week_start, COUNT(*) AS commit_count
        FROM commits
        GROUP BY week_start
        ORDER BY week_start
        """
    ).fetchall()


def fill_missing_weeks(rows):
    """Add zero-count entries for weeks with no commits so gaps show on the chart."""
    counts = {date.fromisoformat(week): count for week, count in rows}
    weeks, values = [], []
    week = min(counts)
    while week <= max(counts):
        weeks.append(week)
        values.append(counts.get(week, 0))
        week += timedelta(weeks=1)
    return weeks, values


def plot_commits_per_week(rows):
    if not rows:
        print("No commits in the database yet. Run `python3 git_insights.py fetch` first.")
        sys.exit(1)

    weeks, counts = fill_missing_weeks(rows)

    plt.figure(figsize=(12, 6))
    # align="edge" makes each bar start on its Monday and span the week.
    plt.bar(weeks, counts, width=6, align="edge", color="skyblue")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xlabel("Week starting")
    plt.ylabel("Number of commits")
    plt.title(f"Commits per Week for GitHub User: {GITHUB_USER}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHART_PATH)
    print(f"Chart saved to {CHART_PATH}")
    plt.show()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("fetch", "chart"):
        print(__doc__)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    initialize_database(conn)

    if sys.argv[1] == "fetch":
        session = make_session()
        for repo in fetch_repositories(session):
            commits = fetch_commits(session, repo["name"])
            save(conn, repo, commits)
            print(f"{repo['name']}: {len(commits)} commits saved.")
    else:
        plot_commits_per_week(commits_per_week(conn))
    conn.close()


if __name__ == "__main__":
    main()
