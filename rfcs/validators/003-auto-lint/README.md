# Auto Linting with GitHub Actions

<!-- Example path: rfcs/validators/003-auto-lint/README.md -->

## Summary
This RFC proposes adding a GitHub Actions workflow that automatically runs `black` and `flake8` on each pull request. The goal is to ensure consistent formatting and to catch linting issues before code is merged.

## Motivation
Manual code style checks slow down reviews and lead to inconsistent formatting. Automating linting encourages contributors to keep the codebase clean and reduces the maintenance burden on reviewers.

## Specification
- A new workflow `lint.yml` runs on pull requests and pushes to `main`.
- The job installs dependencies and executes `black --check` and `flake8`.
- Any formatting or linting errors cause the workflow to fail so issues can be fixed before merging.

## Rationale
Running `black` and `flake8` in CI enforces a single style guide and prevents common errors from reaching production. It also lets contributors focus on functionality rather than formatting.

## Drawbacks
- Initial setup time to configure the workflow.
- Contributors need to run `black` locally to avoid failed builds, which may require additional tooling.

## Adoption Strategy
Start by adding the workflow in check-only mode so developers can see lint warnings. After trialing the process, enforce the checks as required for merging pull requests.

## Unresolved Questions
- Should the workflow automatically commit formatting fixes or just report them?
- What level of flake8 strictness is appropriate for this project?
