Codecov Badge (placeholder)
============================

After your first successful CI run with Codecov, you'll be able to add a badge to your `README.md` that shows code coverage.

Generic placeholder Markdown you can replace with the one Codecov provides for your repository:

```
[![codecov](https://img.shields.io/badge/coverage-0%25-red.svg)](https://codecov.io/gh/<OWNER>/<REPO>)
```

How to get the real badge
- Go to https://codecov.io and open your repository project page after the workflow has uploaded the coverage report.
- Copy the badge markdown from Codecov and paste it into the top of your `README.md`.

If your repository is private, ensure `CODECOV_TOKEN` is configured in GitHub Actions secrets before uploading coverage.
