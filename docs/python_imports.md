# Python Import Strategy

This document explains the import structure for the Side Quest Python project, which uses a monorepo layout.

## Import Patterns

Throughout the codebase, we use the following import pattern:

```python
# Import from other modules within the side_quest_py package
from src.side_quest_py.models import User
from src.side_quest_py.routes.auth_routes import auth_bp
from src.side_quest_py.db_utils import init_db
```

We use absolute imports with the `src.` prefix to ensure consistent imports across the codebase, even when code is executed from different directories.

## Development Setup

### Editor Configuration

The project includes configuration for VS Code and Cursor editors that sets up the correct Python path for imports. These configurations are in:

- `.vscode/settings.json`
- `.cursor/settings.json`

### Terminal Usage

When running Python code from the terminal, you need to ensure the Python interpreter can find the modules. You can do this by:

1. Using the provided `setup_pythonpath.sh` script:
   ```bash
   source setup_pythonpath.sh
   ```

2. Running commands through the script:
   ```bash
   ./setup_pythonpath.sh python -m your_module
   ```

3. Setting `PYTHONPATH` manually:
   ```bash
   export PYTHONPATH=$PYTHONPATH:/path/to/project:/path/to/project/packages/backend:/path/to/project/packages/backend/src
   ```

## Linting and Type Checking

The project uses:
- `pylint` for linting
- `mypy` for type checking
- `flake8` for additional style checks

These tools are configured to recognize the import pattern through:
- `.pylintrc` - Pylint configuration
- `mypy.ini` - Mypy configuration 
- `setup.cfg` - Various tool configurations

## Common Import Issues

If you encounter import errors:

1. Make sure you have the correct Python path set up
2. Check that you're using the standard import pattern with `src.side_quest_py`
3. Restart the language server in your editor (VS Code: Command Palette → "Python: Restart Language Server")
4. If running from the terminal, make sure you've sourced the `setup_pythonpath.sh` script

## Python Package Structure

The package follows a src-layout structure:
```
packages/backend/
├── src/
│   └── side_quest_py/
│       ├── __init__.py
│       ├── config.py
│       ├── models/
│       ├── routes/
│       └── ...
└── tests/
    └── ...
```

This layout allows for clean imports and is a Python packaging best practice. 