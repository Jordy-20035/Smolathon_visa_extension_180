# test_db.py
from app.database import SessionLocal
from app.models import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"User: {user.username}, Role: {user.role}, API Key: {user.api_key}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()