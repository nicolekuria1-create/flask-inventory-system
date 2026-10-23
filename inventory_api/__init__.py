from flask import Flask

from .routes import inventory_bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(TESTING=False)

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(inventory_bp)
    return app
