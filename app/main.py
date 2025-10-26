from flask import Blueprint, render_template, session, redirect, url_for, flash
from . import mysql

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('auth.login'))

    year_level = session.get('year_level')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, code FROM modules WHERE year_level = %s", (year_level,))
    modules = cursor.fetchall()
    cursor.close()

    modules_list = [{'id': m[0], 'name': m[1], 'code': m[2]} for m in modules]

    return render_template('dashboard.html',
                           name=session.get('name'),
                           student_number=session.get('student_number'),
                           year_level=year_level,
                           modules=modules_list)
