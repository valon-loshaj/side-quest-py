from src.side_quest_py import create_app, db

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("All database tables have been created!")