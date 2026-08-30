"""
scripts/create_admin.py — Creates an admin user directly in MongoDB.
Run once to seed the first admin account.
Usage: python scripts/create_admin.py [email] [password] [name]
"""
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bcrypt
from backend.database import get_db
from backend.models.user import UserModel


def create_admin(name: str, email: str, password: str):
    db = get_db()

    # Check if user already exists
    existing = UserModel.find_by_email(db, email)
    if existing:
        if existing.get("role") != "admin":
            UserModel.set_role(db, str(existing["_id"]), "admin")
            print(f"[+] User '{email}' already existed — role updated to admin.")
        else:
            print(f"[!] User '{email}' already exists as admin. Nothing to do.")
        return

    # Hash password
    pw_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")

    now = datetime.datetime.now(datetime.timezone.utc)

    # Insert directly into MongoDB
    doc = {
        "name": name,
        "email": email.strip().lower(),
        "password_hash": hashed,
        "role": "admin",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    result = db["users"].insert_one(doc)

    print(f"\n[+] Admin user created successfully!")
    print(f"    Email    : {email}")
    print(f"    Password : {password}")
    print(f"    Role     : admin")
    print(f"    ID       : {result.inserted_id}")
    print(f"\n    You can now log in at http://localhost:5173/login")


if __name__ == "__main__":
    EMAIL    = sys.argv[1] if len(sys.argv) > 1 else "admin@routeiq.com"
    PASSWORD = sys.argv[2] if len(sys.argv) > 2 else "Admin@123"
    NAME     = sys.argv[3] if len(sys.argv) > 3 else "RouteIQ Admin"

    create_admin(NAME, EMAIL, PASSWORD)
