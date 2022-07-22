import os
import json
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = "Motovilovka"
    DEBUG_TB_ENABLED = False
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "Ensure you set a secret key, this is important!"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASS = os.environ.get("ADMIN_PASS", "pass")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@simple2b.com")

    ALPHABET_FULL = os.environ.get(
        "ALPHABET_FULL", "ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789"
    )

    ALPHABET_UP_DIGITS = os.environ.get(
        "ALPHABET_UP_DIGITS", "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
    )

    AUTH_OTP_ENABLED = json.loads(os.environ.get("AUTH_OTP_ENABLED", "true"))

    PAGE_SIZE = int(os.environ.get("PAGE_SIZE", 17))

    # MQTT
    MOSQUITTO_ADMIN_USER = os.environ.get("MOSQUITTO_ADMIN_USER", "admin")
    MOSQUITTO_ADMIN_PASSWORD = os.environ.get("MOSQUITTO_ADMIN_PASSWORD", "passwd")
    MOSQUITTO_HOST = os.environ.get("MOSQUITTO_HOST", "mqtt")
    MOSQUITTO_PORT = int(os.environ.get("MOSQUITTO_PORT", "1883"))

    # Mail config
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "unknown_user_name")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "no-password")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "sender_name")

    @staticmethod
    def configure(app):
        # Implement this method to do further configuration on your app.
        pass


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEVEL_DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database-devel.sqlite3"),
    )

    # AUTH_OTP_ENABLED = False

    URL_JAVA_SRV = os.environ.get("DEV_URL_JAVA_SRV", None)


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database-test.sqlite3"),
    )

    URL_JAVA_SRV = os.environ.get("DEV_URL_JAVA_SRV", None)


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "database.sqlite3")
    )
    WTF_CSRF_ENABLED = True

    URL_JAVA_SRV = os.environ.get("URL_JAVA_SRV", None)


config = dict(
    development=DevelopmentConfig, testing=TestingConfig, production=ProductionConfig
)
