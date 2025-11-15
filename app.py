from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB = "wishlist.db"

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    if not os.path.exists(DB):
        c = conn()
        cur = c.cursor()
        cur.execute("CREATE TABLE wishlist (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price TEXT, store_link TEXT, created_at TEXT)")
        c.commit()
        c.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    q = request.args.get("q", "").strip()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        price = request.form.get("price","").strip()
        store_link = request.form.get("store_link","").strip()
        if name:
            c = conn()
            cur = c.cursor()
            cur.execute("INSERT INTO wishlist (name, price, store_link, created_at) VALUES (?, ?, ?, ?)",
                        (name, price, store_link, datetime.utcnow().isoformat()+"Z"))
            c.commit()
            c.close()
        return redirect(url_for("index"))
    c = conn()
    cur = c.cursor()
    if q:
        like = f"%{q}%"
        cur.execute("SELECT * FROM wishlist WHERE name LIKE ? OR store_link LIKE ? ORDER BY id DESC", (like, like))
    else:
        cur.execute("SELECT * FROM wishlist ORDER BY id DESC")
    items = cur.fetchall()
    c.close()
    return render_template("index.html", items=items, q=q)

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    c = conn()
    cur = c.cursor()
    cur.execute("DELETE FROM wishlist WHERE id = ?", (item_id,))
    c.commit()
    c.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
