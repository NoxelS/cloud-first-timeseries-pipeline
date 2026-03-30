---
name: make-quality
description: Run code formatters, linters, type checks, and security audits
compatibility: opencode
---

## What I do
Provides the Makefile targets required to enforce codebase standards (formatting, linting, typing, security).

## When to use me
Use this before committing code to ensure it meets project standards, or when fixing code style issues.

## Available Commands
- `make sync` - Synchronize Python dependencies via `uv`. Run this if dependencies change.
- `make format` / `make format-check` - Formats code using `ruff`.
- `make lint` / `make lint-fix` - Lints the codebase with `ruff`. Use `lint-fix` to auto-fix issues.
- `make type-check` - Runs type checking (ignores airflow/).
- `make security` - Runs `bandit` to check for security vulnerabilities.
- `make audit` - Runs `pip-audit` to check for dependency vulnerabilities.