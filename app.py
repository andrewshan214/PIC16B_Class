from flask import Flask, render_template, request
from flask import redirect, url_for, abort
from flask import g
import sqlite3

app = Flask(__name__)

DATABASE = 'messages_db.sqlite'


@app.route('/')
def base():
    return render_template('base.html')


@app.route('/favicon.ico')
def favicon():
    # Optionally provide a favicon
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/getmsg/', methods=['GET'])
def get_message_db():

    '''
    Check whether there is a database called message_db in the g attribute of the app. If not, then connect to that database, ensuring that the connection is an attribute of g. To do this last step, write a line like do g.message_db = sqlite3.connect("messages_db.sqlite")
    Check whether a table called messages exists in message_db, and create it if not. For this purpose, the SQL command CREATE TABLE IF NOT EXISTS is helpful. Give the table an id column (integer), a handle column (text), and a message column (text).
    Return the connection g.message_db.
    '''

    #try to retrieve database connection from global g object
    try:
        db = g.message_db

    #If no connection exists, create a new one
    except AttributeError:
        db = g.message_db = sqlite3.connect(DATABASE)
        db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                handle TEXT,
                message TEXT
            )
        ''')
    #return the database connection
    return db


@app.route('/submit/', methods=['POST'])
def insert_message(request):
    # get message and handle from request
    message = request.form.get('message')
    handle = request.form.get('name')

    db = get_message_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO messages (handle, message) VALUES (?, ?)", (handle, message))
    db.commit()

    db.close()

    return handle, message


@app.route('/submit/', methods=['GET', 'POST'])
def render_submit_template():
    #different methods for diff request methods
    if request.method == 'GET':
        #if 'GET' just render the template
        return render_template('submit.html')
    elif request.method == 'POST':
        handle, message = insert_message(request)
        #render the template with a thank you note
        return render_template('submit.html', thank_you = True, message = message, handle = handle)


@app.route('/random_messages/<int:n>')
def random_message(n):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    cursor.execute("SELECT * FROM messages ORDER BY RANDOM() LIMIT ?", (n,))
    result = cursor.fetchall()

    db.close()

    return result


def render_view_template():
    messages = random_message(5)

    return render_template('view.html', messages = messages)
