from flask import Flask, render_template, request, redirect, flash, session
from app.db import get_db_connection
from app.query import search_params, search_query
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()
ENV_SECRET = os.getenv('SECRET_KEY')

def create_app():
    app = Flask(__name__)
    app.secret_key = ENV_SECRET

    @app.route("/")
    def base():
        return render_template("base.html")
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            
            connection = get_db_connection()
            cursor = connection.cursor(dictionary = True)
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username, ))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                print(user)
                return redirect("/welcome")
            else:
                return "Wrong username or password. Please try again."
        
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
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(password.encode('utf-8'), salt)

            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(query, (username, password))
                connection.commit()

                cursor.close()
                connection.close()

                return redirect("/login")
            
            except:
                cursor.close()
                connection.close()
                return "Error registering. Username may already exist."
            
        return render_template("register.html")
    
    @app.route("/wishlist")
    def wishlist():
        if 'username' not in session:
            return redirect("/")
        
        return render_template("wishlist.html")
    
    @app.route("/search", methods=["GET", "POST"])
    def search():
        if 'username' not in session:
            return redirect("/")
        
        if request.method == "POST" and (request.form['title'] or request.form['authors'] or 
                                         request.form['tag'] or request.form['isbn']):
            session["title"] = request.form['title']
            session["authors"] = request.form['authors']
            session["tag"] = request.form['tag']
            session["isbn"] = request.form['isbn']

            return redirect("/result/1")

        return render_template("search.html")
    
    @app.route("/result/<int:page>")
    def result(page):
        if 'username' not in session:
            return redirect("/")
        
        query = search_query(session["title"], session["authors"], session["tag"], session["isbn"], page)
        params = search_params(session["title"], session["authors"], session["tag"], session["isbn"])

        connection = get_db_connection()
        cursor = connection.cursor(dictionary = True)

        print(query)
        cursor.execute(query, tuple(params))
        books = cursor.fetchall()

        cursor.close()
        connection.close()
        
        return render_template("result.html", tag = session["tag"], books = books, page = page)
    
    @app.route("/rating")
    def rating():
        if 'username' not in session:
            return redirect("/")
        
        return render_template("rating.html")
    
    @app.errorhandler(404)
    def not_found(e):
        return redirect("/")

    return app