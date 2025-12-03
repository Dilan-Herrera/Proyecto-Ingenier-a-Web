from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv 

load_dotenv()

mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.secret_key = os.getenv("SECRET_KEY")

    mongo.init_app(app)

    from .routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from .public_routes import public_bp
    app.register_blueprint(public_bp)

    return app