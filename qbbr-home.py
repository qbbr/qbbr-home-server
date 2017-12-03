import os
import sqlite3
import json
from flask import Flask, request, g

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'qbbr-home.db'),
))
# app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def response(code, data=None):
    return app.response_class(
        status=code,
        mimetype='application/json',
        response=json.dumps(data)
    )


@app.route('/', methods=['GET'])
def default():
    events = {}
    for name, value in query_db('SELECT * FROM events'):
        events[name] = value
    return response(200, events)


@app.route('/<event_name>.json', methods=['GET'])
def get_event(event_name):
    event = query_db('SELECT * FROM events WHERE name = ?',
                     [event_name], one=True)
    if event is None:
        return response(404, {'message': 'event not found'})
    return response(200, {'value': event['value']})


@app.route('/<event_name>.json', methods=['PUT'])
def put_event(event_name):
    request_json = request.get_json()
    value = request_json.get('value')
    if value is None:
        return response(400, {'message': 'value is not defined'})
    db = get_db()
    db.execute('INSERT OR REPLACE INTO events (name, value) VALUES (?, ?)',
               [event_name, value])
    db.commit()
    return response(201)


@app.route('/<event_name>.json', methods=['DELETE'])
def delete_event(event_name):
    db = get_db()
    db.execute('DELETE FROM events WHERE name = ?',
               [event_name])
    db.commit()
    return response(204)
