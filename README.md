# git-insights

Pulls my GitHub commit history through the GitHub REST API, stores it in a
SQLite database, and charts my commit activity per week.

## Why
<!-- TODO: one or two lines in your own words -->

## How it works
<!-- TODO: API -> SQLite (schema.sql) -> SQL aggregation -> matplotlib chart -->

## Run it
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 git_insights.py fetch
python3 git_insights.py chart
```

## Result
<!-- TODO: add commits_per_week.png -->

## What I'd add next
<!-- e.g. pull GitHub Issues from my team project and chart time-to-close -->
