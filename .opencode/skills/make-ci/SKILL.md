---
name: make-ci
description: Run full CI pipeline validation targets via Makefile
compatibility: opencode
---

## What I do
Provides combined Makefile targets that mimic the full CI/CD pipeline or represent a significant "check" on the codebase.

## When to use me
Use this to validate the entire repository state before pushing large PRs or ensuring nothing is fundamentally broken.

## Available Commands
- `make ci` - Full pipeline: sync, format-check, lint, type-check, test, security, and compose-validate.
- `make check` - Shorthand for: format-check, lint, type-check, test.
- `make validate` - Shorthand for: compose-validate, lint, type-check, test.