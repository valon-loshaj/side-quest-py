#!/usr/bin/env python
"""Test MariaDB connection script.

This script tests the connection to the MariaDB database using the DATABASE_URL
environment variable.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

# Get MariaDB connection string from environment or use default
DB_URI = os.environ.get(
    "DATABASE_URL", "mysql+pymysql://side_quest_admin:your_secure_password@localhost/side_quest_dev"
)


def test_connection():
    """Test connection to MariaDB."""
    try:
        engine = create_engine(DB_URI)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar()
            print(f"✅ Successfully connected to MariaDB! Version: {version}")
        return True
    except SQLAlchemyError as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
