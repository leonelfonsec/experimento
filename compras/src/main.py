# src/main.py
import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from .blueprints.operations import operations_blueprint
from .errors.errors import ApiError  # asegúrate de tener src/errors/errors.py

# Carga variables (ajusta ruta si tu .env está en la raíz del repo)
load_dotenv('.env.development')  # o load_dotenv() si tu .env está en la raíz

def create_app():
    app = Flask(__name__)
    app.register_blueprint(operations_blueprint)

    @app.errorhandler(ApiError)
    def handle_exception(err):
        response = {
            "mssg": err.description,
            "version": os.getenv("VERSION", "dev")  # default seguro
        }
        return jsonify(response), err.code

    @app.get("/health")
    def health():
        return {"status": "ok", "version": os.getenv("VERSION", "dev")}

    return app

# Exponer 'app' para gunicorn/docker
app = create_app()

if __name__ == "__main__":
    # Permite: python -m src.main
    app.run(host="0.0.0.0", port=8000, debug=True)