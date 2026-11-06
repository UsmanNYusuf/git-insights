-- Design note: one repo has many commits (one-to-many via repo_id).
CREATE TABLE IF NOT EXISTS repos (
    id   INTEGER PRIMARY KEY,   -- GitHub's repo id
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS commits (
    sha      TEXT PRIMARY KEY,  -- unique per commit, so re-running won't duplicate rows
    repo_id  INTEGER NOT NULL REFERENCES repos(id),
    author   TEXT,
    date     TEXT NOT NULL,     -- ISO 8601 string, e.g. 2026-11-07T14:02:11Z
    message  TEXT
);

-- TODO (optional): add an index on commits(date) and explain why in the README.
