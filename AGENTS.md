# For an agent working in this repo

What this repo is, and what it holds, is in the README. What follows is how to work in it.

- **Tests.** `uv run pytest` runs under testplan (`[tool.pytest.ini_options]` in `pyproject.toml`): it stops at the first failure and runs only the tests whose code, data or packages changed since they passed. `uv run pytest --all` runs every test, once a day. Never turn pytest's cache off (`-p no:cacheprovider`).
- **Ledger.** The design ledger is `ledger/` (`ledger/tree.py`). Load the `quern-ledger` skill before reading or touching it.
- **Pins.** A project that uses this package pins it by commit, so a change here reaches that project only when it moves its pin, which is separate work in its own repo. This repo names no project that uses it.
- **Secrets.** Never print, copy or commit a `.env` or credentials file.
