# ✨ Side Quest ✨

> A modern full-stack app for tracking and managing your side quests! Built with Flask + React + Redux.

## 🚀 Quick Start

### 🐳 Using Docker (Recommended)

The easiest way to get started is with Docker:

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up
```

Then visit:

- 🖥️ **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:5000

### 🧰 Manual Setup

If you prefer setting up manually, you'll need to set up both the frontend and backend:

#### Backend Setup

```bash
# Navigate to backend
cd packages/backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .

# Create .env file with necessary environment variables
cat > .env << EOL
FLASK_APP=src.wsgi
FLASK_ENV=development
SECRET_KEY=your_development_secret_key
DATABASE_URL=mysql+pymysql://side_quest_admin:your_secure_password@localhost/side_quest_dev
FLASK_DEBUG=True
PYTHONPATH=${PYTHONPATH}:$(cd ../../ && pwd):${PWD}:${PWD}/src
EOL

# Ensure instance directory exists
mkdir -p instance

# Initialize the database
flask --app src.wsgi:app init-db

# Seed the database with sample data (optional)
flask --app src.wsgi:app seed-db

# Check database status to verify setup
flask --app src.wsgi:app db-status

# Run the development server
flask --app src.wsgi:app run --debug
```

#### Frontend Setup

```bash
# Navigate to frontend
cd packages/frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

## 🏗️ Project Structure

This is a monorepo project with the following structure:

```
side_quest_py/
├── packages/
│   ├── backend/          # Flask API backend
│   │   ├── src/          # Backend source code
│   │   │   ├── side_quest_py/  # Main application package
│   │   │   └── wsgi.py    # WSGI entry point
│   │   ├── tests/        # Backend tests
│   │   └── ...           # Config files
│   │
│   └── frontend/         # React frontend
│       ├── src/          # Frontend source code
│       │   ├── components/  # React components
│       │   ├── pages/    # Page components
│       │   ├── store/    # Redux store setup
│       │   └── ...       # Other frontend modules
│       └── ...           # Config files
│
├── docker-compose.yml        # Production Docker composition
├── docker-compose.dev.yml    # Development Docker composition
└── ...                       # Root config files
```

## 🛠️ Development Tools

### 🔄 Database Management

```bash
# Initialize the database
flask --app src.wsgi:app init-db

# Seed the database with sample data
flask --app src.wsgi:app seed-db

# Reset the database
flask --app src.wsgi:app reset-db
```

### 🧪 Testing

```bash
# Run backend tests
cd packages/backend
pytest

# Run frontend tests
cd packages/frontend
pnpm test
```

## 🚢 Deployment

### 🐳 Docker Production Deployment

```bash
# Build and start production containers
docker-compose up -d
```

This will:

1. Build the frontend and include it in the backend container
2. Start the production Flask server with Gunicorn

### ⚙️ Environment Configuration

For production, set these environment variables:

```bash
FLASK_ENV=production
SECRET_KEY=<your-secure-production-key>
DATABASE_URL=mysql+pymysql://<username>:<password>@<host>/<database>
```

For more advanced database setups, uncomment the database service in `docker-compose.yml`.

## 🌟 Features

- 🔐 User authentication with JWT
- 📝 Create and manage side quests
- 🗂️ Organize quests with drag-and-drop
- 🎯 Track progress on your personal projects
- 🎨 Modern React interface with Redux state management

## 👩‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the terms of the MIT license.
