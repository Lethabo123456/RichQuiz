from flask import Blueprint, render_template, redirect, session, url_for, request
from . import mysql

main = Blueprint('main', __name__)

# ---------------------- Dashboard ----------------------
@main.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    year_level = session.get('year_level', 1)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, code FROM modules WHERE year_level = %s", (year_level,))
    results = cursor.fetchall()
    cursor.close()

    modules = [{"id": row[0], "name": row[1], "code": row[2]} for row in results]

    return render_template(
        'dashboard.html',
        name=session.get('name'),
        student_number=session.get('student_number'),
        year_level=year_level,
        modules=modules
    )

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



# ---------------------- Show a question (GET) and submit answer (POST) ----------------------
@main.route('/quiz/<int:module_id>/question/<int:current_index>', methods=['GET', 'POST'])
def quiz_question(module_id, current_index):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id, question_text, option_a, option_b, option_c, option_d,
               correct_option, reasoning, difficulty
        FROM questions
        WHERE module_id = %s
        ORDER BY id
    """, (module_id,))
    question_rows = cursor.fetchall()

    if not question_rows:
        cursor.close()
        return "No questions found for this module.", 404

    if current_index < 1 or current_index > len(question_rows):
        cursor.close()
        return "Invalid question index.", 404

    question_data = question_rows[current_index - 1]
    question = {
        "id": question_data[0],
        "text": question_data[1],
        "options": {
            "A": question_data[2],
            "B": question_data[3],
            "C": question_data[4],
            "D": question_data[5]
        },
        "correct": question_data[6],
        "reasoning": question_data[7] or "",
        "difficulty": question_data[8] or "easy"
    }

    cursor.execute("SELECT name, code FROM modules WHERE id = %s", (module_id,))
    module_info = cursor.fetchone()
    cursor.close()

    if not module_info:
        return "Module not found.", 404
    module_name, module_code = module_info

    total = len(question_rows)

    if request.method == 'POST':
        selected_option = request.form.get('option')
        time_taken = int(request.form.get('time_taken', 0))

        if not selected_option:
            # Redisplay question with error if no option selected
            return render_template(
                'quiz.html',
                module_id=module_id,
                module_name=module_name,
                module_code=module_code,
                question=question,
                current_index=current_index,
                total=total,
                error="Please select an option before continuing."
            )

        is_correct = selected_option == question["correct"]

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO user_performance (
                    user_id, module_id, question_id,
                    selected_option, correct_option, is_correct,
                    difficulty, time_taken
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session['user_id'], module_id, question["id"],
                selected_option, question["correct"], is_correct,
                question["difficulty"], time_taken
            ))
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            print(f"❌ Error saving answer: {e}")
        finally:
            cursor.close()

        next_index = current_index + 1
        if next_index > total:
            return redirect(url_for('main.quiz_result', module_id=module_id))
        return redirect(url_for('main.quiz_question', module_id=module_id, current_index=next_index))

    # GET request: show question
    return render_template(
        'quiz.html',
        module_id=module_id,
        module_name=module_name,
        module_code=module_code,
        question=question,
        current_index=current_index,
        total=total,
        error=None
    )


# ---------------------- Quiz result summary ----------------------
@main.route('/quiz/<int:module_id>/result')
def quiz_result(module_id):
    return render_template('result.html', module_id=module_id)
