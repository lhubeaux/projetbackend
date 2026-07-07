"""Classe de base commune aux modèles.

Fournit les colonnes created_at / updated_at (exigées au jour 4) afin de ne
pas les redéclarer sur chaque entité. Les modèles principaux en héritent.

    # class TimestampMixin:
    #     created_at = db.Column(..., default=...)
    #     updated_at = db.Column(..., default=..., onupdate=...)
"""
