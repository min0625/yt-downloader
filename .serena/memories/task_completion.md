# Task Completion

Run these commands before marking a task done (in order):

```
mise run check   # format + lint + type-check + test + pack
```

For quicker feedback on just code quality (skip pack):

```
uv run ruff format .       # format
uv run ruff check --fix .  # lint fix
uv run ty check            # type check
uv run pytest              # tests (expect: 19 collected, all passed)
```

If `mise run check` passes, the task is done.
If failures are pre-existing and unrelated to current changes, document them explicitly.
