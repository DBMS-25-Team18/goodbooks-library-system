from flask import Flask, render_template, request, redirect, flash, session
from app.db import get_db_connection
from dotenv import load_dotenv
import os

load_dotenv()
ENV_SECRET = os.getenv('SECRET_KEY')

def create_app():
    app = Flask(__name__)
    app.secret_key = ENV_SECRET

    @app.route("/")
    def home():
        return render_template("base.html")
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            
            connection = get_db_connection()
            cursor = connection.cursor(dictionary = True)
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                print(user)
                return redirect("/welcome")
            else:
                return "Invalid user. Please try again."
        
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")
    
    @app.route("/welcome")
    def welcome():
        if 'username' not in session:
            return redirect("/")
        return render_template("welcome.html")
    
    @app.route("/register")
    def register():
        return render_template("register.html")
    
    return app