from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session

app = Flask(__name__)

db = SQL("sqlite:///RecetasDB.db")

@app.route("/register", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")

        db.execute("INSERT INTO users (username, hash, cash) VALUES (?, ?, ?)",
                   username, hash, 10000.00)
        return redirect("/login")

    

    return render_template('register.html')