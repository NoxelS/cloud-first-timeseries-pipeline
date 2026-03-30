---
name: make-test
description: Run unit tests, integration tests, and generate coverage reports via Makefile
compatibility: opencode
---

## What I do
Provides commands to run the project's test suite using `pytest` and `uv`.

## When to use me
Use this after writing code to verify changes, or when tasked with checking test coverage.

## Available Commands
- `make test` - Runs the full pytest suite.
- `make test-unit` - Runs ONLY unit tests (excludes integration). Use this for fast feedback loops!
- `make test-integration` - Runs ONLY integration tests.
- `make test-cov` - Runs tests and generates an XML coverage report.