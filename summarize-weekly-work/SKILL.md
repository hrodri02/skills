---
name: summarize-weekly-work
description: Produces a day-by-day bullet-point work summary from git commit history.
disable-model-invocation: true
---

## How to produce the summary

### 1. Resolve the time range

Parse the user's request:

| Phrase | git flags |
|---|---|
| "yesterday" | `--after="yesterday 00:00" --before="today 00:00"` |
| "today" | `--after="today 00:00"` |
| "this week" | `--after="last Monday 00:00"` (Mon → today) |
| "last week" | `--after="2 Mondays ago 00:00" --before="last Monday 00:00"` |
| specific date e.g. "July 10" | `--after="2026-07-10 00:00" --before="2026-07-11 00:00"` |

If the request is ambiguous, default to "this week".

### 2. Fetch the commits

Run this command (adapt the date flags from the table above):

```bash
git log \
  --author="$(git config user.email)" \
  --after="<start>" \
  --before="<end>" \
  --no-merges \
  --pretty=format:"%ad | %s" \
  --date=format:"%Y-%m-%d %A"
```

If no commits are found for the range, say so clearly and stop.

### 3. Group by day

Collect all lines for the same `YYYY-MM-DD` together. Order days chronologically oldest → newest.

### 4. Write the summary

For each day with commits, write a bullet list. Each bullet covers one logical unit of work — a feature added, a bug fixed, a refactor done. Use the commit messages as raw material but group related commits into a single bullet rather than listing each commit separately. Keep each bullet concise (one line when possible).

Skip days with no commits entirely.

## Output format

```
## <Day>, <Month D>

- <what was done>
- <what was done>
```

One `##` section per day. No raw commit hashes. No narrative prose.
