import os
from flask import Flask, render_template, redirect, url_for
import psycopg2

app = Flask(__name__)

def get_db():
    url = os.environ["DATABASE_URL"]
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            emoji VARCHAR(10) NOT NULL,
            votes INTEGER DEFAULT 0
        )
    """)
    cur.execute("SELECT COUNT(*) FROM menu_items")
    if cur.fetchone()[0] == 0:
        items = [
            ("Nasi Lemak", "🍚"),
            ("Mee Goreng", "🍜"),
            ("Roti Canai", "🫓"),
            ("Teh Tarik", "🧋"),
            ("Char Kuey Teow", "🥘"),
            ("Satay", "🍢"),
        ]
        cur.executemany(
            "INSERT INTO menu_items (name, emoji) VALUES (%s, %s)", items
        )
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, emoji, votes FROM menu_items ORDER BY votes DESC")
    items = cur.fetchall()
    cur.close()
    conn.close()
    total = sum(item[3] for item in items) or 1
    return render_template("index.html", items=items, total=total)

@app.route("/vote/<int:item_id>")
def vote(item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE menu_items SET votes = votes + 1 WHERE id = %s", (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

with app.app_context():
    init_db()