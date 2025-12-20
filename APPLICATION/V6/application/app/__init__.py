import secrets
from flask import Flask
from waitress import serve #serveur sur lequel lancer le site
from .routes import main_blueprint

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)  #Clé secrète générée pour chaque session
    app.register_blueprint(main_blueprint)

    return app
