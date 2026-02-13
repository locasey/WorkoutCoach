"""Generate a new invite code for beta access."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import get_db
from services.invite_code_service import InviteCodeService
from models.user import User

OWNER_EMAIL = 'locasey615@gmail.com'


def main():
    db = next(get_db())
    try:
        # Find the admin user to set as creator
        admin = db.query(User).filter(User.email == OWNER_EMAIL).first()
        if not admin:
            print(f"ERROR: Admin user ({OWNER_EMAIL}) not found. Run migration first.")
            sys.exit(1)

        invite = InviteCodeService.generate_code(db, created_by=admin.id)
        print(f"Invite Code: {invite.code}")
        print(f"Expires:     {invite.expires_at.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"Created by:  {admin.email}")
    finally:
        db.close()


if __name__ == '__main__':
    main()
