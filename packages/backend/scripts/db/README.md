# Database Scripts

This directory contains scripts for managing the Side Quest application database.

## Available Scripts

- `init_db.py`: Initializes the database and creates all tables
- `reset_db.py`: Drops all tables and recreates them, effectively resetting the database
- `seed_db.py`: Seeds the database with sample data for development and testing
- `seed_data.py`: Contains functions to generate sample data for the database

## Usage

These scripts can be used in two ways:

### 1. Flask CLI Commands

The scripts are registered as Flask CLI commands and can be run using the following commands:

```bash
# Initialize the database
flask --app src.wsgi:app init-db

# Reset the database (drops all tables and recreates them)
flask --app src.wsgi:app reset-db

# Seed the database with sample data
flask --app src.wsgi:app seed-db

# Check database status
flask --app src.wsgi:app db-status
```

### 2. Direct Execution

Alternatively, you can run the scripts directly:

```bash
# Initialize the database
python -m packages.backend.scripts.db.init_db

# Reset the database
python -m packages.backend.scripts.db.reset_db

# Seed the database
python -m packages.backend.scripts.db.seed_db
```

## Database Configuration

The database configuration is defined in `packages/backend/src/side_quest_py/config.py`. The application uses MariaDB as the database backend with the following default configurations:

- Development: `side_quest_dev` database
- Testing: `side_quest_test` database
- Production: `side_quest` database

The database connection is configured in `config.py` using the DATABASE_URL environment variable:

```python
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "mysql+pymysql://side_quest_admin:your_secure_password@localhost/side_quest_dev"
)
```

You can override these settings by setting the appropriate environment variables:

- `DATABASE_URL`: For development and production
- `TEST_DATABASE_URL`: For testing

For example, in your `.env` file:

```
DATABASE_URL=mysql+pymysql://side_quest_admin:your_secure_password@localhost/side_quest_dev
```

## Migration Support

The application uses Flask-Migrate (Alembic) for database migrations. To create and apply migrations:

```bash
# Create a migration
flask --app src.wsgi:app db migrate -m "Description of changes"

# Apply migrations
flask --app src.wsgi:app db upgrade
```
