#!/user/bin/env python
import click
from app import create_app, db, models
from app.logger import log


app = create_app()


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, m=models)


@app.cli.command()
@click.option("--test-data/--no-test-data", default=False)
def init_db(test_data: bool = False):
    """Init database."""
    from app.controllers import init_db

    db.create_all()
    init_db(test_data)


@app.cli.command()
@click.confirmation_option(prompt="Drop all database tables?")
def drop_db():
    """Drop the current database."""
    db.drop_all()


@app.cli.command()
def create_user():
    """Create user command"""
    username = input("Username: ")

    while True:
        password = input("Password: ")
        password_retry = input("Retry password: ")
        if password != password_retry:
            print("Password mismached. try again.")
            continue
        break
    # TODO user create


@app.cli.command()
def user_list():
    """Get all users"""
    users = models.User.query.all()

    if not users:
        log(log.INFO, "No users")
    
    for user in users:
        log(log.INFO, f"{user}")


@app.cli.command()
def device_list():
    """Get all devices"""
    devices = models.Device.query.all()
    if not devices:
        log(log.INFO, "No devices")

    for device in devices:
        log(log.INFO, device)


@app.cli.command()
def mqtt():
    """Run mqtt listener"""
    from app.controllers import MqttClient

    client = MqttClient()
    log(log.INFO, "enter in loop...")
    client.loop_forever()


if __name__ == "__main__":
    app.run()
