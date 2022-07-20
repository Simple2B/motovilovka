import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from app.logger import log

# instantiate extensions
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(environment="development"):

    from config import config
    from app.views import (
        main_blueprint,
        login_blueprint,
        users_blueprint,
        accounts_blueprint,
        devices_blueprint,
    )
    from app.models import (
        User,
        AnonymousUser,
    )

    # Instantiate app.
    app = Flask(__name__)

    # Set app config.
    env = os.environ.get("FLASK_ENV", environment)
    log(log.INFO, "App environment: %s", env)
    app.config.from_object(config[env])
    config[env].configure(app)

    # Set up extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints.
    app.register_blueprint(login_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(accounts_blueprint)
    app.register_blueprint(devices_blueprint)

    # Set up flask login.
    @login_manager.user_loader
    def get_user(id):
        return User.query.get(int(id))

    login_manager.login_view = "login.login"
    login_manager.login_message_category = "info"
    login_manager.anonymous_user = AnonymousUser

    # Error handlers.
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        log(log.ERROR, "Error code %d", exc.code)
        return render_template("error.html", error=exc), exc.code

    return app
