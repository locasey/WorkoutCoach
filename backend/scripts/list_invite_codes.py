"""List all invite codes with their status."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timezone
from database import get_db
from services.invite_code_service import InviteCodeService
from models.user import User


def main():
    db = next(get_db())
    try:
        codes = InviteCodeService.get_all_codes(db)

        if not codes:
            print("No invite codes found. Run generate_invite_code.py first.")
            return

        print(f"{'Code':<14} {'Status':<10} {'Created':<12} {'Expires':<12} {'Used By':<30}")
        print("-" * 78)

        now = datetime.now(timezone.utc)
        for code in codes:
            if code.is_used:
                status = "USED"
                used_by_user = db.query(User).filter(User.id == code.used_by).first()
                used_by = used_by_user.email if used_by_user else str(code.used_by)
            elif code.expires_at and now >= code.expires_at:
                status = "EXPIRED"
                used_by = "-"
            else:
                status = "ACTIVE"
                used_by = "-"

            created = code.created_at.strftime('%Y-%m-%d') if code.created_at else '-'
            expires = code.expires_at.strftime('%Y-%m-%d') if code.expires_at else '-'

            print(f"{code.code:<14} {status:<10} {created:<12} {expires:<12} {used_by:<30}")

    finally:
        db.close()


if __name__ == '__main__':
    main()
