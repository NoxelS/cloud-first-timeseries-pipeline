---
name: make-utils
description: Run miscellaneous project utility scripts via Makefile
compatibility: opencode
---

## What I do
Provides the Makefile targets that trigger specific internal workflows, client generation, or manual scripts.

## When to use me
Use this when you need to trigger data backfills or re-generate API clients.

## Available Commands
- `make backfill-trigger [START_DATE=YYYY-MM-DD] [END_DATE=YYYY-MM-DD] [REGION=DE-Freiburg]` - Triggers Energy Charts backfill via python script.
- `make openapi-generator-open-charts` - Generates OpenAPI clients using `openapi-python-client`.