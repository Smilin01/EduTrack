from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_key"  # Secret key for session management

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn



# Home page route
@app.route('/')
def index():
    return render_template('login.html')

# Student login
@app.route('/student_login', methods=['POST'])
def student_login():
    roll_number = request.form['roll_number']
    dob = request.form['dob']  # Ensure this is in 'YYYY-MM-DD' format

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE roll_number = ? AND dob = ?', (roll_number, dob)).fetchone()
    conn.close()

    if student:
        session['student_id'] = student['id']
        return redirect(url_for('student_home'))
    else:
        return "Invalid Roll Number or Date of Birth"


# Teacher login page
@app.route('/teacher_login_page')
def teacher_login_page():
    return render_template('teacher_login.html')

# Teacher login
@app.route('/teacher_login', methods=['POST'])
def teacher_login():
    username = request.form['username']
    password = request.form['password']

    if username == "123" and password == "321":
        session['teacher_id'] = username
        return redirect(url_for('teacher_home'))
    else:
        return "Invalid Username or Password"

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    return redirect(url_for('index'))  # Redirect to the login page


# Student home route
@app.route('/student_home')
def student_home():
    if 'student_id' in session:
        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE id = ?', (session['student_id'],)).fetchone()

        # Calculate the overall performance
        total_score = student['tamil'] + student['english'] + student['math'] + student['science'] + student['social']
        max_score = 500  # Assuming each subject is out of 100
        overall_performance = (total_score / max_score) * 100

        # Determine the grade based on overall performance
        if overall_performance == 100:
            grade = 'O'
        elif overall_performance >= 90:
            grade = 'A+'
        elif overall_performance >= 80:
            grade = 'A'
        elif overall_performance >= 70:
            grade = 'B+'
        elif overall_performance >= 60:
            grade = 'B'
        elif overall_performance >= 50:
            grade = 'C'
        elif overall_performance >= 40:
            grade = 'D'
        else:
            grade = 'Fail'

        conn.close()
        return render_template('student_home.html', student=student, overall_performance=overall_performance, grade=grade)
    return redirect(url_for('index'))



# Student dashboard route
@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' in session:
        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE id = ?', (session['student_id'],)).fetchone()

        # Fetch quiz performance data
        quiz_data = conn.execute('SELECT score, quiz_date FROM quiz_scores WHERE student_id = ?', (session['student_id'],)).fetchall()
        quiz_scores = [data['score'] for data in quiz_data]
        quiz_dates = [data['quiz_date'] for data in quiz_data]

        # Calculate the overall performance
        total_score = student['tamil'] + student['english'] + student['math'] + student['science'] + student['social']
        max_score = 500  # Assuming each subject is out of 100
        overall_performance = (total_score / max_score) * 100

        # Determine the grade based on overall performance
        if overall_performance == 100:
            grade = 'O'
        elif overall_performance >= 90:
            grade = 'A+'
        elif overall_performance >= 80:
            grade = 'A'
        elif overall_performance >= 70:
            grade = 'B+'
        elif overall_performance >= 60:
            grade = 'B'
        elif overall_performance >= 50:
            grade = 'C'
        elif overall_performance >= 40:
            grade = 'D'
        else:
            grade = 'Fail'

        conn.close()
        return render_template('student_dashboard.html', student=student, quiz_scores=quiz_scores, quiz_dates=quiz_dates, overall_performance=overall_performance, grade=grade)
    return redirect(url_for('index'))



# Get weakest subject for quiz
def get_weakest_subject(student):
    scores = {
        "Tamil": student['tamil'],
        "English": student['english'],
        "Math": student['math'],
        "Science": student['science'],
        "Social": student['social']
    }
    return min(scores, key=scores.get)  # Find subject with lowest score

# Generate quiz questions using Open Trivia DB
def generate_quiz_questions():
    url = "https://opentdb.com/api.php?amount=10&type=multiple"
    response = requests.get(url)
    data = response.json()

    quiz_questions = []
    for item in data['results']:
        correct_answer = item['correct_answer']

        # Basic explanation logic based on the correct answer
        explanation = f"The correct answer is {correct_answer} because it is factually accurate according to the source of the question."

        question = {
            "text": item['question'],
            "options": item['incorrect_answers'] + [correct_answer],
            "answer": correct_answer,
            "explanation": explanation  # Updated explanation logic
        }
        quiz_questions.append(question)

    return quiz_questions

# Quiz page route
@app.route('/quiz_page')
def quiz_page():
    if 'student_id' in session:
        # Generate quiz questions
        quiz_questions = generate_quiz_questions()

        # Store questions in the session to ensure they are the same on feedback page
        session['quiz_questions'] = quiz_questions

        return render_template('quiz.html', quiz_questions=quiz_questions)
    return redirect(url_for('index'))

# Quiz submission and feedback route
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    # Use the quiz questions stored in the session
    quiz_questions = session.get('quiz_questions', [])
    correct_count = 0
    feedback = []

    # Iterate over each question (assuming there are 10 questions)
    for i in range(1, 11):
        selected_answer = request.form.get(f'answer{i}')  # Dynamically get the answer for each question
        correct_answer = quiz_questions[i-1]['answer']

        if selected_answer == correct_answer:
            correct_count += 1
        else:
            feedback.append({
                'question': quiz_questions[i-1]['text'],
                'selected': selected_answer,
                'correct': correct_answer,
                'explanation': quiz_questions[i-1]['explanation']
            })


    # Save quiz performance to the database
    if 'student_id' in session:
        conn = get_db_connection()
        conn.execute('INSERT INTO quiz_scores (student_id, score, quiz_date) VALUES (?, ?, ?)',
                     (session['student_id'], correct_count, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()

    # Clear quiz questions from session after use to avoid storing them unnecessarily
    session.pop('quiz_questions', None)

    return render_template('quiz_feedback.html', correct_count=correct_count, feedback=feedback)


# Teacher home route
@app.route('/teacher_home', methods=['GET', 'POST'])
def teacher_home():
    conn = get_db_connection()

    # Handle adding a new student
    if request.method == 'POST' and 'add_student' in request.form:
        roll_number = request.form['roll_number']
        name = request.form['name']
        dob = request.form['dob']
        standard = request.form['standard']
        term = request.form['term']
        tamil = request.form['tamil']
        english = request.form['english']
        math = request.form['math']
        science = request.form['science']
        social = request.form['social']

        # Insert the new student into the database
        conn.execute('''
            INSERT INTO students (roll_number, dob, name, standard, term, tamil, english, math, science, social)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (roll_number, dob, name, standard, term, tamil, english, math, science, social))
        conn.commit()

    # Fetch distinct student records to avoid duplication
    students = conn.execute('SELECT DISTINCT id, roll_number, name, dob, standard, term, tamil, english, math, science, social FROM students').fetchall()

    # Prepare to store quiz performance data for each student
    quiz_scores = {}
    quiz_dates = {}

    for student in students:
        student_id = student['id']
        quiz_data = conn.execute('SELECT score, quiz_date FROM quiz_scores WHERE student_id = ?', (student_id,)).fetchall()
        if quiz_data:
            quiz_scores[student_id] = [data['score'] for data in quiz_data]
            quiz_dates[student_id] = [data['quiz_date'] for data in quiz_data]
        else:
            quiz_scores[student_id] = []  # No quiz data for this student
            quiz_dates[student_id] = []  # No quiz dates for this student

    conn.close()
    return render_template('teacher_home.html', students=students, quiz_scores=quiz_scores, quiz_dates=quiz_dates)


# Update Student Data
@app.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    conn = get_db_connection()

    # Update student details based on the form input
    roll_number = request.form['roll_number']
    name = request.form['name']
    dob = request.form['dob']
    standard = request.form['standard']
    term = request.form['term']
    tamil = request.form['tamil']
    english = request.form['english']
    math = request.form['math']
    science = request.form['science']
    social = request.form['social']

    conn.execute('''
        UPDATE students 
        SET roll_number = ?, dob = ?, name = ?, standard = ?, term = ?, tamil = ?, english = ?, math = ?, science = ?, social = ?
        WHERE id = ?
    ''', (roll_number, dob, name, standard, term, tamil, english, math, science, social, student_id))
    conn.commit()
    conn.close()

    return redirect(url_for('teacher_home'))




if __name__ == '__main__':
    app.run(debug=True)
