"""Configuration de l'application, par environnement.

Chaque classe regroupe les réglages d'un contexte. L'app factory reçoit la
classe à utiliser (DevConfig par défaut, TestConfig depuis conftest.py).
Lit les variables d'environnement (documentées dans le README au jour 4).

    # class BaseConfig:
    #     SECRET_KEY = ...
    #     PROMOTION_THRESHOLD = ...        # seuil configurable du passage d'année
    #
    # class DevConfig(BaseConfig):
    #     SQLALCHEMY_DATABASE_URI = "sqlite:///academie.db"
    #     SQLALCHEMY_ECHO = True           # log SQL pour la chasse au N+1 (jour 2)
    #
    # class TestConfig(BaseConfig):
    #     TESTING = True
    #     SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"   # base isolée des tests
"""
