# CLAUDE.md - Cloud-First Time Series Pipeline

This repository implements an event-driven modular data platform for collecting external data, generating features, and preparing data for ML pipelines. It uses `uv` for Python dependency management (with workspaces), `docker compose` for local infrastructure (Kafka, Postgres, Airflow), and `make` for task execution.

## 🛠️ Agent Skills & Tools
**Important:** There are pre-configured OpenCode skills available for testing, quality control, infrastructure, and deployment! Load them using the `skill` tool when appropriate:
- `make-test`: Run unit/integration tests and coverage.
- `make-quality`: Run formatters (`ruff`), linters, type checks (`ty`), and security audits (`bandit`).
- `make-infra`: Manage the docker-compose stack and volumes.
- `make-kafka`: Manage local Kafka topics and consumer groups.
- `make-ci`: Run full CI pipeline validation targets.
- `make-utils`: Trigger data backfills or generate API clients.

## 🏗️ Build, Test, and Lint Commands
- **Install/Sync**: `make sync` (Uses `uv sync` under the hood)
- **Format**: `make format` (ruff)
- **Lint**: `make lint` (ruff) & `make type-check` (ty)
- **Test All**: `make test`
- **Test Unit**: `make test-unit` (Excludes integration tests, highly recommended for fast iteration loops!)
- **Test Single File**: `uv run pytest path/to/test_file.py`
- **Test Single Function**: `uv run pytest path/to/test_file.py::test_function_name`
- **Full Check**: `make check` (format-check, lint, type-check, test)

## 💻 Code Style & Standards
- **Python Version**: Target is Python 3.10+ (`>=3.10,<4.0`).
- **Formatting**: Max line length is 120. Strict reliance on `ruff` (`preview = true`). Run `make format` instead of manually spacing.
- **Typing**: Strict type hints required for all function signatures. Enforced by `flake8-annotations` (`ANN`), except in `airflow/dags/*`.
- **Naming Conventions**: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants. Test files/functions must start with `test_`.
- **Imports**: Absolute imports preferred. Handled by `ruff` (`I` rule).
- **Error Handling**: Use specific exception catches (no bare `except:`). Enforced by `tryceratops` (`TRY`) and `flake8-return` (`RET`).
- **Security**: Never hardcode secrets; use env vars. Enforced by `flake8-bandit` (`S`). No `assert` in production code (allowed in tests).
- **Commits**: Use Conventional Commits for all commit messages (e.g., `feat: `, `fix: `, `chore: `, `docs: `, `refactor: `). Keep messages clear, concise, and focused on the "why".

## 🐳 Infrastructure & Kafka
- **Deploy/Teardown**: `make deploy` / `make down`. Use `make hard-deploy` or `make hard-down` to destroy volumes/state.
- **Logs**: `make compose-logs`
- **Data Ingestion**: Services should publish events to Kafka topics instead of directly calling other services.

## 🧠 Proactiveness and Context
- **Understand Before Modifying**: Use `grep` and `glob` to thoroughly read related code. Look at `shared/` for common models before reinventing them.
- **No Assumptions**: Never assume a dependency exists. Always check `pyproject.toml` workspace members or dependency lists first.
- **Self-Verification**: Write tests for your code, run the specific test using `uv run pytest <file>`, and ensure `make check` passes before declaring tasks complete.

## 📐 Architecture & Principles
1. **Event-driven & Stateless**: All ingestion flows through Kafka. Containers must be stateless; persistent data belongs in Postgres or Kafka.
2. **Single Responsibility**: Each service does one thing (e.g., `eurostat_collector` fetches EUROSTAT data and publishes events to Kafka).
3. **Repository Structure**:
   - `infra/`: Docker and local environment setup.
   - `services/`: Microservices for data collection (fetch -> normalize -> publish).
   - `airflow/`: DAGs for orchestration. Must remain thin orchestration layers; no heavy data processing logic here.
   - `shared/`: Reusable utilities (Kafka, schemas). Must remain small.
   - `tests/`: Unit tests (near code), Integration, and E2E tests.
   - `scripts/`: Developer utilities (do not contain production logic).
4. **Events**: Should be immutable, small, and self-describing (key, timestamp, payload, metadata).

*Note: As an agent, prefer small incremental improvements over large refactors. Keep services isolated and maintain test coverage.*