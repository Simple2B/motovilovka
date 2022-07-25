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
def user_list():
    """Get all users"""
    users = models.User.query.all()

    if not users:
        log(log.INFO, "No users")

    for user in users:
        print(f"{user}")


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

    client = MqttClient(client_id="listener")
    log(log.INFO, "enter in loop...")
    client.loop_forever()


@app.cli.command()
@click.option("--topic", default="test_type/test_name", help="topic path")
@click.option("--value", default=1, help="data value")
def write_topic(topic: str, value: int):
    """Write test MQTT topic"""
    import json
    from app.controllers import MqttClient
    from app.models import Account

    log(log.INFO, "Write [%s]:[%s]", topic, value)
    account: Account = Account.query.all()[-1]
    client = MqttClient(client_id="shell", account=account)
    payload = json.dumps(dict(value=value), indent=2).encode()
    log(log.INFO, "Payload [%s]", payload)
    res = client.publish(f"{account.mqtt_login}/{topic}", payload=payload)
    print(res)


@app.cli.command()
@click.option("--account", default="admin", help="topic user name")
@click.option("--name", default="device", help="device name")
@click.option("--value", default=1, help="data value")
def test_value(account: str, name: str, value: int):
    """Set TEST_VALUE value"""
    import json
    from app.controllers import MqttClient
    from app.models import Account

    acc: Account = Account.query.filter(Account.mqtt_login == account).first()
    if not acc:
        log(log.ERROR, "Account [%s] not found", account)
        return
    client = MqttClient(client_id="shell", account=acc)
    payload = json.dumps(dict(value=value), indent=2).encode()
    log(log.INFO, "Payload [%s]", payload)
    client.publish(f"{account}/TEST_VALUE/{name}", payload=payload)


if __name__ == "__main__":
    app.run()
