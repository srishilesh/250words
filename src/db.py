import sqlite3

import click
from flask import current_app, g

def get_db():
    """
    g - special global store object which is unique for each request - used as proxy that can store data during application context
    current_app - points to app handling request
    connect() - connects with sqlite file
    sqlite3.Row - tells rows to behave as dicts
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    open_resource - opens file relative to app file
    db - returns a db connection
    executescript - reads the db file and loads it
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
def init_db_command():
    """
    click - defines a CLI command to initialized the db - clear data & create new tables
    """
    init_db()
    click.echo("Initialized the database")

def init_app(app):
    """
    teardown_appcontext() - tells to call the function when cleaning up. Called when exiting "with app.app_context()"
    add_command() - new cli command while running
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)