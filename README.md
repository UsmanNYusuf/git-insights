# git-insights

Pulls my GitHub commit history through the GitHub REST API, stores it in a
SQLite database, and charts my commit activity per week.

## Why
I wanted to see my coding habits and practise an API-to-database-to-insight pipeline.

## How it works
- Data comes from the GitHub REST API
- Stored in 2 SQLite tables: repos and commits
- SQL groups the commits by week; Python fills in weeks with no commits as zero, and matplotlib draws a bar chart as a PNG
- Pagination allows for all results to be shown, showing 100 items per page and following the next link until no pages remain

## Design Decisions
- I've made sha the primary key because a sha is a hash which is unique to a commit, meaning that a second fetch would not store duplicate commits.
- Weeks with no commits appear on the chart so gaps in activity are visible rather than collapsed and the timeline isn't distorted
- Bugs found in review were fixed with the assistance of an AI coding agent; changes were reviewed and tested.
- Tokens are read from an environment variable so the secret never ends up in the code or on GitHub

## Run it
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GITHUB_TOKEN=your_token_here	# optional: raises the rate limit
python3 git_insights.py fetch
python3 git_insights.py chart
```

## Result
![Commits per week](commits_per_week.png)

## What I'd add next
- A per-repo breakdown
- Pull GitHub Issues data and chart time-to-close
