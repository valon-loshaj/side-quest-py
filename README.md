# Side Quest Python

A Flask-based application for managing side quests.

## Development Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file based on the `.env.example` template:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your environment:

```
# Key environment variables:
FLASK_ENV=development  # Options: development, testing, production
SECRET_KEY=your_secure_key_here
DATABASE_URL=sqlite:///instance/side_quest_dev.db
```

The application uses different database configurations based on the environment:
- **Development**: `sqlite:///instance/side_quest_dev.db` (default)
- **Testing**: `sqlite:///instance/side_quest_test.db`
- **Production**: Set `DATABASE_URL` to a production database (PostgreSQL recommended)

### 4. Initialize the database

```bash
# Create database tables
flask --app src.side_quest_py init-db

# Optionally seed the database with sample data
flask --app src.side_quest_py seed-db
```

To reset the database (drop all tables and recreate them):
```bash
flask --app src.side_quest_py reset-db
```

### 5. Run the development server

```bash
flask --app src.side_quest_py run --debug
```

### 6. Verify the application is running

Visit http://127.0.0.1:5000/hello in your browser. You should see "Hello, Side Quest!"

You can also check the database connection status at http://127.0.0.1:5000/health

## Project Structure

- `src/side_quest_py/`: Application package
  - `__init__.py`: Application factory
  - `config.py`: Environment-specific configurations
  - `db.py`: Database utility functions
  - `models/`: Database models
  - `routes/`: API routes organized by blueprint

## Database Management

### Database Migrations

When you make changes to your models, create a migration:

```bash
flask --app src.side_quest_py db migrate -m "Description of changes"
```

Apply the migration:

```bash
flask --app src.side_quest_py db upgrade
```

### Database Environments

#### Development

The development database is used when `FLASK_ENV=development`. It uses SQLite by default.

#### Testing

To run with the testing database:

```bash
FLASK_ENV=testing flask --app src.side_quest_py run
```

This is useful for integration tests that need a clean database.

#### Production

For production deployment, set these environment variables:

```
FLASK_ENV=production
SECRET_KEY=your_secure_production_key
DATABASE_URL=your_production_database_url
```

For production, consider using PostgreSQL:
```
DATABASE_URL=postgresql://username:password@hostname:5432/side_quest
```
