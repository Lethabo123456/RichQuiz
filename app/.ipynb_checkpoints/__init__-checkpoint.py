from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    
    # Configuration for MySQL
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'quiz_db'  # We'll create this DB next in phpMyAdmin
    
    mysql.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app
 
