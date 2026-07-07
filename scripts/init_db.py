"""Script d'initialisation de la base : python init_db.py [--delete]"""

import sys
from app import create_app
from app.dal.database import db

app = create_app()

with app.app_context():
    if "--delete" in sys.argv:
        db.drop_all()
        print("❌ Tables supprimées.")
    db.create_all()
    print("✅ Tables créées.")
