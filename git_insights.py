import sqlite3
import sys
import requests
import matplotlib.pyplot as plt

GITHUB_USER = "UsmanNYusuf"
API = f"https://api.github.com/users/{GITHUB_USER}/repos"
DB_PATH = "git_insights.db"

def get_json(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        sys.exit(1)

def fetch_repositories():
    return get_json(API)

def fetch_commits(repo_name):
    commits_api = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/commits"
    return get_json(commits_api)

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT,
            updated_at TEXT,
            pushed_at TEXT,
            stargazers_count INTEGER,
            watchers_count INTEGER,
            forks_count INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_id INTEGER NOT NULL,
            sha TEXT NOT NULL,
            author_name TEXT,
            author_email TEXT,
            message TEXT,
            date TEXT,
            FOREIGN KEY (repo_id) REFERENCES repositories (id)
        )
    ''')
    conn.commit()
    conn.close()

def save(conn, repo, commits):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO repositories (id, name, description, created_at, updated_at, pushed_at, stargazers_count, watchers_count, forks_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        repo['id'],
        repo['name'],
        repo.get('description'),
        repo['created_at'],
        repo['updated_at'],
        repo['pushed_at'],
        repo['stargazers_count'],
        repo['watchers_count'],
        repo['forks_count']
    ))
    repo_id = cursor.lastrowid
    for commit in commits:
        cursor.execute('''
            INSERT INTO commits (repo_id, sha, author_name, author_email, message, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            repo_id,
            commit['sha'],
            commit['commit']['author']['name'],
            commit['commit']['author']['email'],
            commit['commit']['message'],
            commit['commit']['author']['date']
        ))
    conn.commit()

def commits_per_week(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT strftime('%Y-%W', date) AS week, COUNT(*) AS commit_count
        FROM commits
        GROUP BY week
        ORDER BY week
    ''')
    return cursor.fetchall()

def plot_commits_per_week(data):
    weeks = [row[0] for row in data]
    commit_counts = [row[1] for row in data]

    plt.figure(figsize=(12, 6))
    plt.bar(weeks, commit_counts, color='skyblue')
    plt.xlabel('Week (Year-Week)')
    plt.ylabel('Number of Commits')
    plt.title(f'Commits per Week for GitHub User: {GITHUB_USER}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("fetch", "chart"):
        print(__doc__)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    initialize_database(conn)

    if sys.argv[1] == "fetch":
        for repo in fetch_repositories():
            commits = fetch_commits(repo['name'])
            save(conn, repo, commits)
            print(f"{repo['name']}: {len(commits)} commits saved.")
    else: 
        data = commits_per_week(conn)
        plot_commits_per_week(data)
    conn.close()

if __name__ == "__main__":
    main()

