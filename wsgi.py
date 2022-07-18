#!/user/bin/env python
import click
from app import create_app, db, models


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
    from app.models import User

    username = input("username: ")
    password = input("password: ")
    User(username=username, password=password).save()


@app.cli.command()
def remove_user():
    """Remove user"""
    from app.models import User

    username = input("Username: ")
    user: User = User.query.filter_by(username=username).first()
    if user:
        user.deleted = True
        user.save()
    else:
        print(f"User [{username}] not found")


if __name__ == "__main__":
    app.run()
