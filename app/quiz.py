import os
import random
import joblib
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from time import time
from . import mysql

quiz_bp = Blueprint('quiz', __name__)

# ---------------------- LOAD ML MODEL ---------------------- #
model_path = os.path.join(os.path.dirname(__file__), "../ml/quiz_predictor.pkl")
try:
    quiz_model = joblib.load(model_path)
    print("✅ Quiz prediction model loaded successfully!")
except Exception as e:
    print("❌ Failed to load quiz model:", e)
    quiz_model = None

def predict_correct(difficulty, time_taken):
    """Predict if the user will answer correctly and return probability."""
    if quiz_model is None:
        return None, None
    difficulty_map = {"Easy": 1, "Medium": 2, "Hard": 3}
    diff_numeric = difficulty_map.get(difficulty, 1)
    import pandas as pd
    df = pd.DataFrame({"difficulty": [diff_numeric], "time_taken": [time_taken]})
    pred = quiz_model.predict(df)[0]
    prob = quiz_model.predict_proba(df)[0][1]
    # Convert to native Python types
    return int(pred), float(prob)

# ---------------------- START QUIZ ---------------------- #
@quiz_bp.route('/start/<int:module_id>')
def start_quiz(module_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, code FROM modules WHERE id = %s", (module_id,))
        module_info = cursor.fetchone()
        cursor.close()

        if not module_info:
            abort(404, f"No module found with ID {module_id}")
        module_name, module_code = module_info

        session['quiz'] = {
            'module_id': int(module_id),
            'module_name': module_name,
            'module_code': module_code,
            'current_index': 0,
            'answers': [],
            'score': 0,
            'previous_difficulty': 'Easy',
            'question_ids': [],
            'question_start_time': time()
        }
        session['quiz_start_time'] = time()
        return redirect(url_for('quiz.quiz_question'))

    except Exception as e:
        print("❌ Error starting quiz:", e)
        abort(500, "Internal server error while starting quiz.")

# ---------------------- ADAPTIVE QUESTION FETCH ---------------------- #
def get_next_question(module_id, difficulty, used_ids):
    try:
        cursor = mysql.connection.cursor()
        used_ids_tuple = tuple(used_ids) if used_ids else (0,)
        cursor.execute("""
            SELECT id FROM questions 
            WHERE module_id = %s AND difficulty = %s AND id NOT IN %s
        """, (module_id, difficulty, used_ids_tuple))
        available = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return random.choice(available) if available else None
    except Exception as e:
        print("❌ Error in adaptive question selection:", e)
        return None

# ---------------------- DISPLAY A QUESTION ---------------------- #
@quiz_bp.route('/question', methods=['GET', 'POST'])
def quiz_question():
    quiz = session.get('quiz')
    if not quiz:
        return redirect(url_for('main.index'))

    if quiz['current_index'] >= 10:
        return redirect(url_for('quiz.quiz_results'))

    if request.method == 'POST':
        selected_option = request.form.get('option')
        question_id = quiz['question_ids'][-1]
        question = get_question_by_id(question_id)

        if not selected_option:
            return render_template(
                'quiz.html',
                question=build_question_dict(question),
                module_id=quiz['module_id'],
                module_name=quiz['module_name'],
                module_code=quiz['module_code'],
                current_index=quiz['current_index'] + 1,
                total=10,
                error="Please select an answer."
            )

        correct_option = question[6]
        is_correct = selected_option == correct_option
        time_taken = int(time() - quiz.get('question_start_time', time()))

        # Predict correctness using ML model
        pred, confidence = predict_correct(quiz['previous_difficulty'], time_taken)
        print(f"Predicted correctness: {pred}, confidence: {confidence:.2f}" if pred is not None else "ML prediction unavailable")

        # Adjust difficulty using ML confidence
        new_difficulty = adjust_difficulty(quiz['previous_difficulty'], is_correct, ml_confidence=confidence)

        # Store answers, ensuring all values are native Python types
        quiz['answers'].append({
            'question_id': int(question[0]),
            'text': question[1],
            'options': {
                'A': question[2],
                'B': question[3],
                'C': question[4],
                'D': question[5]
            },
            'selected_option': selected_option,
            'correct_option': correct_option,
            'reasoning': question[7] or "",
            'difficulty': question[8] or "Easy",
            'is_correct': bool(is_correct),
            'time_taken': int(time_taken),
            'ml_prediction': int(pred) if pred is not None else None,
            'ml_confidence': float(confidence) if confidence is not None else None
        })

        if is_correct:
            quiz['score'] += 1
        quiz['previous_difficulty'] = new_difficulty
        quiz['current_index'] += 1
        quiz['question_start_time'] = time()
        session['quiz'] = quiz

    if quiz['current_index'] >= 10:
        return redirect(url_for('quiz.quiz_results'))

    next_question_id = get_next_question(
        quiz['module_id'],
        quiz['previous_difficulty'],
        quiz['question_ids']
    )

    if not next_question_id:
        return redirect(url_for('quiz.quiz_results'))

    quiz['question_ids'].append(next_question_id)
    quiz['question_start_time'] = time()
    session['quiz'] = quiz
    question = get_question_by_id(next_question_id)

    return render_template(
        'quiz.html',
        question=build_question_dict(question),
        module_id=quiz['module_id'],
        module_name=quiz['module_name'],
        module_code=quiz['module_code'],
        current_index=quiz['current_index'] + 1,
        total=10,
        error=None,
        show_explanations=False
    )

# ---------------------- SHOW RESULTS ---------------------- #
@quiz_bp.route('/results')
def quiz_results():
    quiz = session.pop('quiz', None)
    if not quiz:
        return redirect(url_for('main.index'))

    end_time = time()
    start_time = session.pop('quiz_start_time', end_time)
    total_time_taken = int(end_time - start_time)
    user_id = session.get('user_id')

    if user_id:
        try:
            cursor = mysql.connection.cursor()
            for answer in quiz['answers']:
                cursor.execute("""
                    INSERT INTO user_performance (
                        user_id, module_id, question_id,
                        difficulty, is_correct, time_taken, attempted_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (
                    int(user_id),
                    int(quiz['module_id']),
                    int(answer['question_id']),
                    answer['difficulty'],
                    bool(answer['is_correct']),
                    int(answer['time_taken'])
                ))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            print("❌ Failed to save performance:", e)
            mysql.connection.rollback()

    correct_count = int(quiz['score'])
    total = len(quiz['answers'])
    score_percentage = round((correct_count / total) * 100, 2)
    passed = correct_count / total >= 0.5
    user_answers = [a['selected_option'] for a in quiz['answers']]

    difficulty_stats = {
        'Easy': {'correct': 0, 'total': 0, 'total_time': 0},
        'Medium': {'correct': 0, 'total': 0, 'total_time': 0},
        'Hard': {'correct': 0, 'total': 0, 'total_time': 0}
    }

    for answer in quiz['answers']:
        diff = answer.get('difficulty', 'Easy').capitalize()
        if diff not in difficulty_stats:
            diff = 'Easy'
        difficulty_stats[diff]['total'] += 1
        difficulty_stats[diff]['total_time'] += int(answer.get('time_taken', 0))
        if answer.get('is_correct'):
            difficulty_stats[diff]['correct'] += 1

    feedback = []
    for diff, stats in difficulty_stats.items():
        if stats['total'] == 0:
            continue
        accuracy = stats['correct'] / stats['total']
        avg_time = stats['total_time'] / stats['total'] if stats['total'] else 0

        if accuracy < 0.5:
            feedback.append(f"⚠️ You struggled with **{diff.lower()}** questions. Review these concepts again.")
        elif avg_time > 30:
            feedback.append(f"⏱ You took too long on **{diff.lower()}** questions. Practice to improve speed.")
        else:
            feedback.append(f"✅ Good performance on **{diff.lower()}** questions.")

    if not feedback:
        feedback.append("🧠 Excellent work across all levels!")

    return render_template(
        'result.html',
        correct_count=correct_count,
        total=total,
        score_percentage=score_percentage,
        passed=passed,
        questions=quiz['answers'],
        user_answers=user_answers,
        module_id=quiz['module_id'],
        module_name=quiz['module_name'],
        module_code=quiz['module_code'],
        time_taken=total_time_taken,
        difficulty_stats=difficulty_stats,
        ai_feedback=feedback,
        show_explanations=True
    )

# ---------------------- UTILS ---------------------- #
def adjust_difficulty(current, is_correct, ml_confidence=None):
    """Adjust difficulty based on correctness and optional ML prediction confidence."""
    levels = ['Easy', 'Medium', 'Hard']
    idx = levels.index(current)

    if ml_confidence is not None:
        if ml_confidence >= 0.8 and idx < 2:
            return levels[idx + 1]
        elif ml_confidence <= 0.3 and idx > 0:
            return levels[idx - 1]

    if is_correct and idx < 2:
        return levels[idx + 1]
    elif not is_correct and idx > 0:
        return levels[idx - 1]

    return current

def get_question_by_id(qid):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, question_text, option_a, option_b, option_c, option_d,
               correct_option, reasoning, difficulty
        FROM questions WHERE id = %s
    """, (qid,))
    row = cursor.fetchone()
    cursor.close()
    return row

def build_question_dict(row):
    return {
        'id': int(row[0]),
        'text': row[1],
        'options': {
            'A': row[2],
            'B': row[3],
            'C': row[4],
            'D': row[5]
        },
        'correct_option': row[6],
        'reasoning': row[7] or "",
        'difficulty': row[8] or "Easy"
    }
