# Side Quest Py

A Python adventure quest project using Flask and SQLAlchemy.

## Setup and Installation

### Development Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd side_quest_py
   ```

2. Run the setup script:
   ```bash
   ./scripts/setup_dev.sh
   ```

   This script will:
   - Create a virtual environment
   - Install dependencies
   - Set up pre-commit hooks
   - Install the package in development mode
   - Create a default .env file

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

### Manual Setup

If you prefer to set up manually:

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Running the Application

### Development Mode

Start the Flask development server:

```bash
flask --app src/wsgi.py run --debug
```

Or use VS Code:
- Press Ctrl+Shift+P (or Cmd+Shift+P on macOS)
- Select "Tasks: Run Task"
- Choose "Run Development Server"

### Production Mode

For production deployment, use Docker:

```bash
docker-compose up -d
```

## Development Tools

### VS Code Tasks

The following tasks are available in VS Code:

- **Run Tests**: Run all tests
- **Run Tests with Coverage**: Run tests and generate coverage report
- **Lint with pylint**: Check code quality with pylint
- **Format with Black**: Format code with Black
- **Sort imports with isort**: Sort imports with isort
- **Type check with mypy**: Run mypy type checking
- **Run Development Server**: Start the Flask development server

To run a task:
- Press Ctrl+Shift+P (or Cmd+Shift+P on macOS)
- Select "Tasks: Run Task"
- Choose the task you want to run

### VS Code Launch Configurations

The following launch configurations are available:

- **Python: Flask Development**: Run Flask in development mode
- **Python: Flask Production**: Run Flask in production mode
- **Python: Current File**: Run the current file
- **Python: Debug Tests**: Debug the current test file
- **Python: All Tests**: Run and debug all tests

To use a launch configuration:
- Press F5 or go to the Run menu
- Select the configuration from the dropdown
- Click the Run button

### Pre-commit Hooks

The following pre-commit hooks are installed:

- trailing-whitespace: Remove trailing whitespace
- end-of-file-fixer: Ensure files end with a newline
- check-yaml: Check YAML syntax
- check-toml: Check TOML syntax
- debug-statements: Check for debugger imports and py37+ breakpoint()
- check-merge-conflict: Check for merge conflict strings
- isort: Sort imports
- black: Format code
- flake8: Check code quality
- mypy: Check types
- pytest-check: Run tests

### Running Tests

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src --cov-report=term
```

Run a specific test file:

```bash
pytest tests/test_models/test_quest.py
```

Run tests with a specific mark:

```bash
pytest -m "not slow"
```

## Continuous Integration

The project uses GitHub Actions for CI/CD. The following checks are run:

- Lint with flake8
- Check formatting with black
- Sort imports with isort
- Type check with mypy
- Run tests on multiple Python versions

## Project Structure

```
side_quest_py/
├── .github/
│   └── workflows/          # GitHub Actions workflows
├── .vscode/
│   ├── launch.json         # VS Code launch configurations
│   └── tasks.json          # VS Code tasks
├── docs/                   # Documentation
├── instance/               # Instance-specific data (SQLite database)
├── scripts/                # Utility scripts
├── src/
│   ├── side_quest_py/      # Main package
│   │   ├── models/         # Database models
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic
│   │   ├── __init__.py     # Flask app factory
│   │   └── config.py       # Configuration
│   └── wsgi.py             # WSGI entry point
├── tests/
│   ├── test_models/        # Model tests
│   ├── test_routes/        # API route tests
│   └── conftest.py         # Test fixtures
├── .env                    # Environment variables
├── .flake8                 # Flake8 configuration
├── .isort.cfg              # isort configuration
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── pyproject.toml          # Project metadata
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Development dependencies
```
