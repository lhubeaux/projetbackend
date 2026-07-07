"""App factory de l'Académie de Sorcellerie.

Responsabilité de ce fichier :
    - définir create_app(config) : construit et retourne l'application Flask
    - charger la configuration (voir config.py)
    - relier les extensions à l'app (db.init_app(app))
    - enregistrer les blueprints du dossier routes/
    - enregistrer les handlers d'erreur (voir app/common/errors.py)

Aucune route ni logique métier ici : uniquement le montage de l'application.

    # def create_app(config_class=DevConfig):
    #     app = Flask(__name__)
    #     app.config.from_object(config_class)
    #     db.init_app(app)
    #     ... enregistrement des blueprints ...
    #     return app
"""
from flask import Flask
from app.dal.database import db
from config import DevConfig
from app.dal import models


def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app

