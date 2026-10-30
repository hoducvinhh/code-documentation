# Contributing to Code Documentation Skill

Thank you for your interest in contributing to `code-documentation-skill`! We welcome contributions that improve documentation workflows, expand framework detection, and enhance test coverage.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please be respectful, constructive, and collaborative in all communications.

---

## Development Principles

When modifying or adding features, adhere strictly to these core tenets:

1. **Python Standard Library Only**: Helper scripts under `skills/code-documentation/scripts/` must NOT depend on any external package from PyPI. They must execute out-of-the-box on standard Python 3.10+ environments across Linux, macOS, and Windows.
2. **Deterministic Outputs**: Scripts should produce predictable, structured JSON outputs when requested and exit with meaningful status codes (`0` for success, non-zero for errors/failures).
3. **Cross-Platform Compatibility**: Use `os.path` / `pathlib` for file paths and handle both Windows (`\`) and POSIX (`/`) directory separators cleanly.
4. **Comprehensive Test Coverage**: Any new feature or bug fix in the scripts must be accompanied by unit tests in `tests/`.

---

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/code-documentation.git
   cd code-documentation
   ```

2. **Verify your Python installation**:
   ```bash
   python --version  # Must be Python 3.10 or higher
   ```

3. **Run the test suite**:
   ```bash
   python -m unittest discover -s tests -p "test_*.py" -v
   ```

---

## Project Structure

- `skills/code-documentation/SKILL.md`: The main agent instruction file conforming to the [Agent Skills](https://agentskills.io) specification.
- `skills/code-documentation/references/`: Reference guides read by agents for specific documentation domains.
- `skills/code-documentation/scripts/`: Deterministic Python helper scripts.
- `skills/code-documentation/assets/`: Template markdown files.
- `tests/`: Automated unit tests and test fixtures.

---

## Submitting Pull Requests

1. Create a descriptive branch:
   ```bash
   git checkout -b feature/detect-rust-cargo
   ```
2. Make your changes adhering to existing code conventions.
3. Run the unit test suite and self-validation scripts:
   ```bash
   python -m unittest discover -s tests -p "test_*.py" -v
   python skills/code-documentation/scripts/check-links.py .
   python skills/code-documentation/scripts/validate-docs.py .
   python skills/code-documentation/scripts/detect-secrets.py .
   ```
4. Commit your changes with clear, concise commit messages.
5. Push to your fork and submit a Pull Request describing your changes, motivation, and test verification.
