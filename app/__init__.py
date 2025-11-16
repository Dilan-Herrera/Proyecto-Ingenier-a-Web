from flask import Flask
from flask_pymongo import PyMongo
import os

mongo = PyMongo()


def create_app():
    app = Flask(__name__)

    mongo_uri = os.environ.get("MONGO_URI")

    if not mongo_uri:
        mongo_uri = "mongodb://localhost:27017/techadvisor_db"

    app.config["MONGO_URI"] = mongo_uri

    app.secret_key = os.environ.get("SECRET_KEY", "clave_dev_super_insegura")

    mongo.init_app(app)

    from .routes import admin_bp
    app.register_blueprint(admin_bp)

    return app
