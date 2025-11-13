CI (GitHub Actions)
====================

This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` which runs unit tests on push and pull requests against `main`/`master`.

Workflow behavior
- Runs on `ubuntu-latest`.
- Tests run on Python 3.10 and 3.11.
- Installs dependencies from `requirements.txt` and runs `pytest -q`.
- Uploads artifacts (current directory) after the job completes.

How to customize
- To add coverage reporting, include `coverage` in `requirements.txt` and update the `Run tests` step to produce a coverage report and upload it.
 - Coverage: this workflow runs `pytest --cov=app --cov-report=xml` and uploads `coverage.xml` as an artifact.
- To add linting, add a step that installs and runs `flake8` or `ruff` before tests.
 - Linting: the workflow runs `ruff` as a lint step; fix issues locally by running `python -m ruff check .`.
 - Linting: the workflow runs `ruff` as a lint step; fix issues locally by running `python -m ruff check .`.

Codecov
-------
The workflow uploads a coverage report (`coverage.xml`) and uploads it to Codecov using the `codecov/codecov-action`. For public repositories Codecov can accept uploads without a token; for private repositories set a `CODECOV_TOKEN` secret in the repository settings.

To add Codecov badge to your `README.md` after CI runs successfully, follow Codecov instructions and add the markdown badge they provide.

Why this helps
- Automatically runs tests on pull requests so regressions are caught early.
- Ensures a consistent test environment across contributors.
