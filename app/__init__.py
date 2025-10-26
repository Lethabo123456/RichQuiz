import os
from flask import Flask

# Use PyMySQL as MySQLdb
import pymysql
pymysql.install_as_MySQLdb()

from flask_mysqldb import MySQL

# Create MySQL instance (global)
mysql = MySQL()

def create_app():
    """Factory pattern to create and configure the Flask app."""
    app = Flask(__name__)

    # ---------------------- MySQL Configuration ----------------------
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'quiz_db')

    # ---------------------- Flask Configuration ----------------------
    app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
    app.config['SESSION_TYPE'] = 'filesystem'

    # Initialize MySQL with app
    mysql.init_app(app)

    # ---------------------- Register Blueprints ----------------------
    try:
        from .main import main as main_bp
        from .auth import auth_bp
        from .quiz import quiz_bp
    except ImportError as e:
        print(f"Error importing blueprints: {e}")
        raise

    app.register_blueprint(main_bp)                     # Default routes
    app.register_blueprint(auth_bp)                     # Auth routes
    app.register_blueprint(quiz_bp, url_prefix='/quiz') # Quiz routes

    return app
