import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()
db_config = {
    'host': 'localhost',
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': 'goodbook_db'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print("Error connecting to MySQL:", e)
        return None