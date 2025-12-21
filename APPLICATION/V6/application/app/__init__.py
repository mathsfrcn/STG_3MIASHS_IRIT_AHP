import secrets
from flask import Flask
from .routes import main_blueprint

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)  # Secrect key for each simulation
    app.register_blueprint(main_blueprint)

    return app
