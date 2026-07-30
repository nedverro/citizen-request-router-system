# app.py
# Dashboard Flask pour visualiser les notifications

import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("notifications.db")
    conn.row_factory = sqlite3.Row
    return conn

# ─────────────────────────────────────────
# Page 1 : Statistiques générales
# ─────────────────────────────────────────
@app.route("/")
def index():
    conn = get_db()

    total      = conn.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
    auto_route = conn.execute("SELECT COUNT(*) FROM notifications WHERE decision='auto_route'").fetchone()[0]
    manuel     = conn.execute("SELECT COUNT(*) FROM notifications WHERE decision='manual_review'").fetchone()[0]
    en_attente = conn.execute("SELECT COUNT(*) FROM notifications WHERE statut='en_attente'").fetchone()[0]

    conn.close()

    stats = {
        "total":      total,
        "auto_route": auto_route,
        "manuel":     manuel,
        "en_attente": en_attente
    }

    return render_template("index.html", stats=stats)

# ─────────────────────────────────────────
# Page 2 : Liste des notifications
# ─────────────────────────────────────────
@app.route("/notifications")
def notifications():
    conn = get_db()
    data = conn.execute("""
        SELECT * FROM notifications
        ORDER BY id ASC
    """).fetchall()
    conn.close()
    return render_template("notifications.html", notifications=data)

if __name__ == "__main__":
    app.run(debug=True)