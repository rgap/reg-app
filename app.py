import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)

DATABASE = 'participants.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def index():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM participants")
    participants = cur.fetchall()
    return render_template('index.html', participants=participants)

@app.route('/register', methods=['POST'])
def register():
    db = get_db()
    phone = request.form.get('phone')
    skills = request.form.get('skills')
    
    db.execute("INSERT INTO participants (phone, skills) VALUES (?, ?)", (phone, skills))
    db.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)