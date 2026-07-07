"""Instance SQLAlchemy partagée.

Isolée dans ce fichier neutre pour éviter les imports circulaires :
les modèles importent `db` d'ici, et l'app factory le relie à l'application
via db.init_app(app). Ce fichier ne dépend de rien d'autre.

    # from flask_sqlalchemy import SQLAlchemy
    # db = SQLAlchemy()
"""
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()