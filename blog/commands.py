# -*- coding: utf-8 -*-
import click

from blog import app, db
from blog.models import User, Article


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    name = 'Wang Yubo'
    articles = [
        {'title': 'My Neighbor Totoro', 'date': '88-01-01', 'text': 'Good Day!'},
        {'title': 'Dead Poets Society', 'date': '89-01-01', 'text': 'Nice Day!'},
        {'title': 'A Perfect World', 'date': '93-01-01', 'text': 'Good Weather!'},
        {'title': 'Leon', 'date': '94-01-01', 'text': 'Nice Weather!'},
        {'title': 'Mahjong', 'date': '96-01-01', 'text': 'Good Day!'},
        {'title': 'Swallowtail Butterfly', 'date': '96-01-01', 'text': 'Good Day!'},
        {'title': 'King of Comedy', 'date': '99-01-01', 'text': 'Good Day!'},
        {'title': 'Devils on the Doorstep', 'date': '99-01-01', 'text': 'Good Day!'},
        {'title': 'WALL-E', 'date': '08-01-01', 'text': 'Good Day!'},
        {'title': 'The Pork of Music', 'date': '12-01-01', 'text': 'Good Day!'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in articles:
        article = Article(title=m['title'], date=m['date'], text=m['text'])
        db.session.add(article)

    db.session.commit()
    click.echo('Done.')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')
