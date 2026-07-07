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
