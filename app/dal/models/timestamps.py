"""Classe d'horodatage commune aux modèles.

Fournit les colonnes created_at / updated_at (exigées au jour 4) afin de ne
pas les redéclarer sur chaque entité. Les modèles principaux en héritent.
"""

from datetime import datetime, timezone
from app.dal.database import db
from sqlalchemy.orm import Mapped, mapped_column
#note : utilisation de Flask-SQLAlchemy et pas de Alchemy pur. db.Model est équivalent à la classe declarative_base() utilisée dans les projets précédents. Elle automatiquement créée par le init_app donc pas besoin de l'ajouter.

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    #lambda pour que ça soit au moment de l'inserstion et non au moment du lancement du serveur
    
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )