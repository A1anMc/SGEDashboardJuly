from app.db.init_db import init_db

def main() -> None:
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully.")

if __name__ == "__main__":
    main() 