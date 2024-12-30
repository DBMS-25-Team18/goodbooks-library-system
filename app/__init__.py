from flask import Flask, render_template, request, redirect, flash, session
from app.db import get_db_connection
from app.query import search_params, search_query
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()
ENV_SECRET = os.getenv("SECRET_KEY")

def create_app():
    app = Flask(__name__)
    app.secret_key = ENV_SECRET

    @app.route("/")
    def base():
        return render_template("home.html")
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(password.encode("utf-8"), salt)

            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(query, (username, password))
                connection.commit()

                cursor.close()
                connection.close()

                flash("Successfully registered! Please login.", "success")
                return redirect("/login")
            
            except:
                cursor.close()
                connection.close()
                flash("Error registering. Username may already exist.", "danger")
            
        return render_template("register.html")
    
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

            if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                print(user)
                return redirect("/welcome")
            else:
                flash("Incorrect username or password!", "danger")
        
        return render_template("login.html")
    
    @app.route("/welcome")
    def welcome():
        if "username" not in session:
            return redirect("/")
        
        return render_template("welcome.html")
    
    @app.route("/search", methods=["GET", "POST"])
    def search():
        if "username" not in session:
            return redirect("/")
        
        if request.method == "POST" and (request.form["title"] or request.form["authors"] or 
                                         request.form["tag"] or request.form["isbn"]):
            session["title"] = request.form["title"]
            session["authors"] = request.form["authors"]
            session["tag"] = request.form["tag"]
            session["isbn"] = request.form["isbn"]

            return redirect("/result/1")

        return render_template("search.html")
    
    @app.route("/result/<int:page>")
    def result(page):
        if "username" not in session:
            return redirect("/")
        
        if page <= 0:
            return redirect("/result/1")

        query = search_query(session["title"], session["authors"], session["tag"], session["isbn"], page)
        params = search_params(session["title"], session["authors"], session["tag"], session["isbn"])

        connection = get_db_connection()
        cursor = connection.cursor(dictionary = True)

        cursor.execute(query, tuple(params))
        books = cursor.fetchall()

        cursor.close()
        connection.close()
        
        return render_template("result.html", books = books, page = page)
    
    @app.route("/addwish/<int:id>", methods=["POST"])
    def addwish(id):
        if "username" not in session:
            return redirect("/")
        
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            query = "INSERT INTO to_reads (user_id, books_id) VALUES (%s, %s)"
            cursor.execute(query, (session["user_id"], id))
            connection.commit()

            cursor.close()
            connection.close()
        
        except:
            cursor.close()
            connection.close()
            flash("This book is already in the Wishlist.", "danger")
        
        return redirect("/wishlist")
    
    @app.route("/wishlist")
    def wishlist():
        if "username" not in session:
            return redirect("/")
        
        query = "SELECT * FROM users AS u, books AS b, to_reads AS r WHERE u.id = %s AND u.id = r.user_id AND r.books_id = b.id"

        connection = get_db_connection()
        cursor = connection.cursor(dictionary = True)

        cursor.execute(query, (session["user_id"], ))
        books = cursor.fetchall()

        cursor.close()
        connection.close()
        
        return render_template("wishlist.html", books = books)
    
    @app.route("/delwish/<int:id>", methods=["POST"])
    def delwish(id):
        if "username" not in session:
            return redirect("/")
        
        if request.form["method"] == "DELETE":
            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                query = "DELETE FROM to_reads WHERE user_id = %s and books_id = %s"
                cursor.execute(query, (session["user_id"], id))
                connection.commit()

                cursor.close()
                connection.close()
            
            except:
                cursor.close()
                connection.close()
                flash("This book is not in your Wishlist.", "danger")
        
        return redirect("/wishlist")
    
    @app.route("/rating/<int:id>")
    def rating(id):
        if "username" not in session:
            return redirect("/")
        
        query = "SELECT * FROM books AS b WHERE b.id = %s"

        connection = get_db_connection()
        cursor = connection.cursor(dictionary = True)

        cursor.execute(query, (id, ))
        book = cursor.fetchone()

        cursor.close()
        connection.close()
        
        return render_template("rating.html", book = book)
    
    @app.route("/subrate/<int:id>", methods=["POST"])
    def subrate(id):
        if "username" not in session:
            return redirect("/")
        
        rating = request.form["rating"]
        
        insert_query = "INSERT INTO ratings (user_id, books_id, rating) VALUES (%s, %s, %s)"
        update_query = "UPDATE ratings SET rating = %s WHERE user_id = %s AND books_id = %s"

        connection = get_db_connection()
        cursor = connection.cursor(dictionary = True)

        try:
            cursor.execute(insert_query, (session["user_id"], id, rating))
            connection.commit()

        except:
            cursor.execute(update_query, (rating, session["user_id"], id))
            connection.commit()

        finally:
            cursor.close()
            connection.close()
        
        return redirect("/rated")
    
    @app.route("/rated")
    def rated():
        if "username" not in session:
            return redirect("/")
        
        query = "SELECT * FROM users AS u, books AS b, ratings AS r WHERE u.id = %s AND u.id = r.user_id AND r.books_id = b.id"

        connection = get_db_connection()
        cursor = connection.cursor(dictionary = True)

        cursor.execute(query, (session["user_id"], ))
        books = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template("rated.html", books = books)
    
    @app.route("/delrate/<int:id>", methods=["POST"])
    def delrate(id):
        if "username" not in session:
            return redirect("/")
        
        if request.form["method"] == "DELETE":
            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                query = "DELETE FROM ratings WHERE user_id = %s and books_id = %s"
                cursor.execute(query, (session["user_id"], id))
                connection.commit()

                cursor.close()
                connection.close()
            
            except:
                cursor.close()
                connection.close()
                flash("This book is not Rated by you yet.", "danger")
        
        return redirect("/rated")
    
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")
    
    @app.errorhandler(404)
    def not_found(e):
        return redirect("/")

    return app