from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import mysql  # MySQL instance from __init__.py

auth_bp = Blueprint('auth', __name__)

# --- Register Route (GET + POST) ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        student_number = request.form.get('student_number')
        password = request.form.get('password')
        year_level = request.form.get('year_level')

        if not all([name, student_number, password, year_level]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        try:
            year_level = int(year_level)
            if year_level < 1 or year_level > 5:
                flash('Year level must be between 1 and 5.', 'danger')
                return redirect(url_for('auth.register'))
        except ValueError:
            flash('Year level must be a number.', 'danger')
            return redirect(url_for('auth.register'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE student_number = %s", (student_number,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Student number already exists.', 'warning')
            cur.close()
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (name, student_number, password, year_level) VALUES (%s, %s, %s, %s)",
            (name, student_number, hashed_pw, year_level)
        )
        mysql.connection.commit()
        cur.close()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# --- Login Route (GET + POST) ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_number = request.form.get('student_number')
        password = request.form.get('password')

        if not student_number or not password:
            flash('Student number and password are required.', 'danger')
            return redirect(url_for('auth.login'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, student_number, password, year_level FROM users WHERE student_number = %s", (student_number,))
        user = cur.fetchone()
        cur.close()

        if user:
            user_id, name, student_number_db, hashed_pw, year_level = user
            print(f"Fetched user: {user}")  # Debugging statement

            if check_password_hash(hashed_pw, password):
                session['user_id'] = user_id
                session['student_number'] = student_number_db
                session['name'] = name
                session['year_level'] = year_level

                print("Redirecting to dashboard")  # Debugging statement
                return redirect(url_for('main.dashboard'))

        flash('Invalid student number or password.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


# --- Logout Route ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# --- Reset Password Route (GET + POST) ---
@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        student_number = request.form.get('student_number')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not all([student_number, new_password, confirm_password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.reset_password'))

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE student_number = %s", (student_number,))
        user = cur.fetchone()

        if not user:
            flash('Student number not found.', 'danger')
            cur.close()
            return redirect(url_for('auth.reset_password'))

        hashed_pw = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password = %s WHERE student_number = %s", (hashed_pw, student_number))
        mysql.connection.commit()
        cur.close()

        flash('Password reset successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')
