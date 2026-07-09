"""App factory de l'Académie de Sorcellerie.

Responsabilité : construire et retourner l'application Flask, charger la
configuration, relier les extensions, enregistrer les blueprints et les
handlers d'erreur. Aucune route ni logique métier ici.
"""
from flask import Flask
from app.dal.database import db
from config import DevConfig
from app.dal import models
from app.api.routes import ALL_BLUEPRINTS
from app.common.errors import register_error_handlers

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)
    register_error_handlers(app)

    return app
# 