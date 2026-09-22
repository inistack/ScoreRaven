import click
from app import db
from app.models.user import User

def register_cli(app):
    @app.cli.command('create-user')
    @click.option('--email', required=True)
    @click.option('--name', required=True)
    @click.option('--role', required=True, type=click.Choice(["admin", "grader"]))
    @click.password_option()
    def create_user(email, name, role, password):
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo(f"A user with email {email} already exists.")
            return
        user = User(email=email, name=name, role=role, is_verified=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        click.echo(f"Created {role} account: {email}")