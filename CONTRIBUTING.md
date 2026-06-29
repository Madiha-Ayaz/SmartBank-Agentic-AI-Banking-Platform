# Contributing to SmartBank

Thank you for considering contributing to SmartBank — the Agentic AI Banking Operations Platform for Pakistan. This document provides guidelines and expectations for all contributions.

---

## Table of Contents

1. [How to Report Issues](#how-to-report-issues)
2. [Development Setup](#development-setup)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Pull Request Process](#pull-request-process)
5. [Commit Message Conventions](#commit-message-conventions)
6. [Code Review Checklist](#code-review-checklist)
7. [Testing Requirements](#testing-requirements)

---

## How to Report Issues

### Bug Reports

Open a [GitHub Issue](https://github.com/your-org/smartbank/issues) with the following template:

```markdown
**Description:**
Clear, concise description of the bug.

**Steps to Reproduce:**
1. Go to '...'
2. Run '...'
3. See error

**Expected Behaviour:**
What you expected to happen.

**Actual Behaviour:**
What actually happened, including full error output.

**Environment:**
- Python version: 3.10 / 3.11
- OS: Windows / macOS / Linux
- SmartBank version: (from package.json)
- UiPath Studio version: (if relevant)
- LLM provider: anthropic / openai

**Logs:**
Relevant error logs or stack traces.

**Possible Fix:**
Optional — suggestions for the root cause or fix.
```

### Feature Requests

Open a GitHub Issue with label `enhancement`:

```markdown
**Problem:**
What problem does this feature solve?

**Proposed Solution:**
How should the feature work?

**Alternatives Considered:**
What other approaches have you considered?

**Additional Context:**
Screenshots, mockups, or references.
```

### Security Vulnerabilities

Do **not** open public issues for security vulnerabilities. Email `security@smartbank.ai` with details. See [SECURITY.md](SECURITY.md) for our responsible disclosure policy.

---

## Development Setup

### Prerequisites

- Python 3.10 or 3.11
- Node.js 20+ (for OpenAPI validation and UI work)
- Git
- A virtual environment tool (`venv` or `conda`)

### Step-by-Step

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/smartbank.git
cd smartbank

# Add upstream remote
git remote add upstream https://github.com/your-org/smartbank.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install development dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt  # If available, otherwise:
pip install pytest pytest-cov pytest-mock requests-mock
pip install flake8 flake8-docstrings
pip install Pillow requests

# Copy environment file and configure
cp .env.example .env

# Verify setup
python -m pytest agents/ document-ai/ robots/ -v --tb=short
flake8 agents/ document-ai/ robots/ --max-line-length=120 --statistics
```

### Branch Naming

- `feat/<short-description>` — new features
- `fix/<short-description>` — bug fixes
- `docs/<short-description>` — documentation changes
- `refactor/<short-description>` — code refactoring
- `test/<short-description>` — test additions or improvements
- `chore/<short-description>` — maintenance tasks

---

## Code Style Guidelines

### Python

SmartBank follows [PEP 8](https://peps.python.org/pep-0008/) with a maximum line length of 120 characters (configured in `setup.cfg` or `tox.ini`).

```ini
# setup.cfg
[flake8]
max-line-length = 120
extend-ignore = E203, W503
exclude = .git, __pycache__, .pytest_cache, venv
```

#### Rules

- **Indentation:** 4 spaces. No tabs.
- **Imports:** Group in this order, separated by a blank line:
  1. `from __future__ import annotations`
  2. Standard library (`os`, `json`, `datetime`, etc.)
  3. Third-party (`pytest`, `requests`, `PIL`, etc.)
  4. Local application imports
- **Type hints:** Required for all function signatures and public class attributes. Use `from __future__ import annotations` for forward references.
- **Docstrings:** Google-style docstrings for all public modules, classes, and functions:
  ```python
  def process_message(message: str, language: str) -> Response:
      """Process a customer message and return a structured response.

      Args:
          message: The raw user input text.
          language: The detected or declared language code.

      Returns:
          A Response dataclass with text, language, module, and escalation info.
      """
  ```
- **Naming conventions:**
  - `snake_case` for variables, functions, methods
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
  - Single leading underscore for internal/private members
- **Dataclasses:** Use `@dataclass` for data containers. Prefer immutable (frozen) dataclasses where possible.
- **Enums:** Use `class Status(str, Enum)` pattern for string-compatible enums.
- **Error handling:** Be explicit. Catch specific exceptions, not bare `except:` blocks. Log exceptions with `logger.exception()` when re-raising.

### BPMN

- All workflow definitions must conform to BPMN 2.0 XML schema.
- Naming convention for process IDs: `PascalCase` (e.g. `CardBlockWorkflow`).
- Each workflow must have exactly one `startEvent` and at least one `endEvent`.
- Every `serviceTask` must reference a defined `implementation` or `operationRef`.
- Gateways (`exclusiveGateway`, `parallelGateway`) must have named outgoing sequence flows.
- Lane names must match team or system identifiers (e.g. `CBS_Lane`, `AI_Lane`, `Human_Lane`).
- Error boundary events must be attached to all service tasks that call external systems.
- Documentation elements on every task: include purpose, input/output, and error handling notes.

### YAML

- Use 2-space indentation. No tabs.
- Line length: maximum 120 characters.
- Strings: Use double quotes only when required (special characters, colons, etc.). Prefer unquoted.
- Lists: Use hyphen + space format. Align nested lists at the same indent level.
- Anchors and aliases: Use `&` and `*` sparingly — prefer duplication for readability in configuration files.
- Comments: Use `#` with a space. Place on their own line above the described element.
- File naming: `kebab-case.yaml` (e.g. `gateway-config.yaml`, `ci.yml`).

---

## Pull Request Process

1. **Create a branch** from `main` following the naming convention above.

2. **Make your changes** following code style guidelines. Include tests for all new functionality and bug fixes.

3. **Run all tests locally** before pushing:
   ```bash
   python -m pytest agents/ document-ai/ robots/ -v --tb=long
   flake8 agents/ document-ai/ robots/ --max-line-length=120 --statistics
   ```

4. **Commit your changes** with a descriptive message following the commit message convention (see below).

5. **Push your branch** and open a pull request against `main`:
   ```bash
   git push origin feat/my-feature
   ```

6. **Complete the PR template** — include a clear description of the change, testing instructions, screenshots if UI changes, and links to related issues.

7. **Ensure CI passes** — the GitHub Actions pipeline runs lint, test, validate, and build stages. All must pass before review.

8. **Request review** from at least one maintainer. Address all review comments. Use `fixup!` commits for review feedback (they will be squashed before merge).

9. **Squash and merge** — once approved and CI is green, the maintainer will squash your commits into a single commit with a conventional commit message.

### PR Title Format

```
<type>(<scope>): <short description>
```

Examples:
- `feat(classifier): add Urdu language intent patterns`
- `fix(cbs-connector): handle token expiry with auto-refresh`
- `docs(readme): add performance benchmark table`

---

## Commit Message Conventions

SmartBank follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Usage |
|------|-------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Changes that do not affect code meaning (formatting, whitespace) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `chore` | Maintenance, build, CI, dependency updates |
| `ci` | CI/CD configuration changes |

### Scopes

| Scope | Area |
|-------|------|
| `assistant` | `agents/customer-assistant/` |
| `classifier` | `agents/classification-agent/` |
| `pipeline` | `document-ai/` |
| `fraud` | `document-ai/fraud-detection/` |
| `cbs` | `robots/cbs-connector/` |
| `audit` | `robots/audit-logger/` |
| `notifications` | `robots/notification-dispatcher/` |
| `pdf` | `robots/document-generation/` |
| `api` | `api/` |
| `ci` | `cicd/` |
| `docs` | Documentation files |
| `config` | Configuration files |

### Examples

```
feat(assistant): add Senior Citizen Account product info in Urdu
fix(cbs): handle HTTP 408 timeout with exponential backoff
docs(api): add PATCH /customers/{id}/identity endpoint documentation
test(pipeline): add integration test for fraud scoring with all indicators
ci: add BPMN XML validation step to CI pipeline
refactor(fraud): extract indicator weights into configurable dictionary
```

---

## Code Review Checklist

Reviewers will verify the following for every pull request:

### Correctness
- [ ] Does the code do what it claims to do?
- [ ] Are edge cases handled (empty inputs, null values, network failures)?
- [ ] Are error conditions properly logged and surfaced?
- [ ] Do the tests cover the change adequately?

### Design
- [ ] Does the change follow existing patterns and conventions?
- [ ] Is the code appropriately modular — not too large, not too fragmented?
- [ ] Are public APIs well-named and intuitive?
- [ ] Are there no breaking changes to public interfaces without deprecation strategy?

### Security
- [ ] Are secrets and API keys never logged, printed, or committed?
- [ ] Is input validated and sanitized (no SQL injection, no path traversal)?
- [ ] Are proper authentication and authorization checks in place?
- [ ] Is sensitive data masked in logs and API responses?

### Performance
- [ ] Are database queries indexed appropriately?
- [ ] Are external API calls wrapped with timeout and retry logic?
- [ ] Are large data structures (images, documents) processed efficiently?

### Style
- [ ] Does the code follow PEP 8 (Python) or project YAML conventions?
- [ ] Are type hints present and correct?
- [ ] Are docstrings present for public modules, classes, and functions?
- [ ] Are there no commented-out code blocks, print statements, or debug artifacts?

### Tests
- [ ] Do all existing tests pass?
- [ ] Are new tests added for all new functionality?
- [ ] Do tests cover both success and failure paths?
- [ ] Are tests deterministic (no flaky tests)?

---

## Testing Requirements

### General Rules

- All new code must have corresponding tests.
- Minimum line coverage threshold: **80%** (enforced by CI).
- Tests must be deterministic — no reliance on external services, network availability, or timing.
- Use `pytest` as the test runner.
- Use `pytest-mock` for mocking external dependencies.
- Use `pytest-cov` for coverage measurement.

### Test Structure

Tests live alongside the code they test:

```
agents/customer-assistant/
  assistant.py
  tests/
    __init__.py
    test_assistant.py

document-ai/
  pipeline.py
  tests/
    __init__.py
    test_pipeline.py

robots/cbs-connector/
  robot.py
  tests/  (if applicable)
    test_cbs_connector.py
```

### Test Content

Each test file should cover, at minimum:

1. **Happy path** — the primary successful use case
2. **Error handling** — invalid inputs, network failures, permission errors
3. **Boundary conditions** — edge values, empty states, large inputs
4. **State mutations** — verifying that operations have the intended side effects

For UiPath robots, each robot includes 5 defined unit test scenarios (documented in each robot's module docstring):

| Robot | Scenarios |
|-------|-----------|
| CBS Connector | Happy path, invalid credentials, account not found, token expired, CBS timeout |
| Audit Logger | Happy path, hash chain continuity, integrity check detects tamper, concurrent append, missing log directory |
| Notification Dispatcher | Happy path, invalid email, SMS template not found, WhatsApp rate limit, unsupported channel |
| Document Generator | Happy path, unsupported letter type, empty account ID, Urdu text rendering, output file missing |

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=agents --cov=document_ai --cov=robots --cov-report=term-missing

# Run specific module tests
python -m pytest agents/customer-assistant/tests/
python -m pytest document-ai/tests/
python -m pytest robots/ --no-header

# Run a specific test class
python -m pytest agents/customer-assistant/tests/test_assistant.py::TestProductEducation -v

# Run tests matching a keyword
python -m pytest -k "fraud"

# Generate JUnit XML for CI integration
python -m pytest --junitxml=results.xml
```

---

## Getting Help

- Open a [Discussion](https://github.com/your-org/smartbank/discussions) for questions
- Join our [Slack channel](https://smartbank-community.slack.com/) (invite link in discussions)
- Read the [architecture document](architecture/architecture.md) for system design context

---

*This document is maintained by the SmartBank core team. We review and update it quarterly. Last updated: June 2026.*
