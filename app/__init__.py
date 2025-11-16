from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = "mongodb+srv://Dilan:UDLA@clusteringweb.lyhmd0l.mongodb.net/techadvisor_db?retryWrites=true&w=majority&appName=ClusterIngWEB"

    app.secret_key = "clave_secreta"

    mongo.init_app(app)

    from .routes import admin_bp
    app.register_blueprint(admin_bp)

    return app