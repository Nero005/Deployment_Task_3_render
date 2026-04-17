import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

def get_db():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, message, created_at FROM entries ORDER BY created_at DESC")
    entries = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", entries=entries)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    message = request.form["message"]
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO entries (name, message) VALUES (%s, %s)", (name, message))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run()

with app.app_context():
    init_db()