from flask import abort, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from model import app, db, User, Question, QuizResult
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


# Setting up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Protect the admin orutes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# admimn dashboard
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    questions = Question.query.all()
    return render_template('admin.html', users=users, questions=questions)
@app.route('/make_admin/<int:user_id>')
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f"{user.username} is now an admin.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    QuizResult.query.filter_by(user_id=user.id).delete()
    db.session.commit()

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.question = request.form['question']
        question.option_a = request.form['option_a']
        question.option_b = request.form['option_b']
        question.option_c = request.form['option_c']
        question.option_d = request.form['option_d']
        question.answer = request.form['answer']
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_question.html', question=question)

@app.route('/delete_question/<int:question_id>')
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password using pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken!', 'danger')
            return redirect(url_for('register'))

        # Check if this is the first user
        is_admin = False
        if not User.query.first():  # First user is the admin
            is_admin = True

        # Create new user
        new_user = User(username=username, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username does not exist.', 'danger')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Incorrect password. Please try again.', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Login successful!', 'success')
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('quiz'))

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Quiz route (with authentication)
@app.route('/quiz', methods=["GET", "POST"])
@login_required
def quiz():
    if request.method == "POST":
        session['score'] = 0
        session['questions_answered'] = 0

        # Redirect to the quiz questions
        return redirect(url_for('next_question', question_number=1))
    questions = Question.query.all()
    session['total_questions'] = len(questions)
    return render_template('quiz.html', questions=questions)

# Next question route
@app.route('/question/<int:question_number>', methods=["GET", "POST"])
@login_required
def next_question(question_number):
    question = Question.query.get(question_number)
    if not question:
        return redirect(url_for('result'))

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = question.answer
        if user_answer == correct_answer:
            session['score'] += 1
        session['questions_answered'] += 1
        return redirect(url_for('next_question', question_number=question_number + 1))

    options = [question.option_a, question.option_b, question.option_c, question.option_d]
    return render_template('question.html', question=question, question_number=question_number, options=options, total_questions=Question.query.count())

# Submit quiz
@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    score = session.get('score', 0)
    total_questions = session.get('total_questions', 0)

    # Create new quiz result entry
    quiz_result = QuizResult(user_id=current_user.id, score=score, total_questions=total_questions)
    db.session.add(quiz_result)
    db.session.commit()

    # Reset session values after submitting quiz
    session.pop('score', None)
    session.pop('questions_answered', None)

    flash('Quiz submitted successfully!', 'success')
    return redirect(url_for('quiz_results'))

# Results route
@app.route('/result')
@login_required
def result():
    score = session.get('score', 0)
    total = Question.query.count()

    # Save the result to the database
    result = QuizResult(score=score, total=total, user_id=current_user.id)
    db.session.add(result)
    db.session.commit()

    # Fetch scores
    user_high_score = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.score.desc()).first()
    leaderboard = QuizResult.query.order_by(QuizResult.score.desc()).limit(10).all()

    return render_template(
        'result.html',
        score=score,
        total=total,
        user_high_score=user_high_score.score if user_high_score else 0,
        leaderboard=leaderboard,
        enumerate=enumerate
    )

# Route to display the form and handle form submission
@app.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Capture form data
        question_text = request.form.get('question')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        correct_answer = request.form.get('answer')

        # Validate the form
        if not all([question_text, option_a, option_b, option_c, option_d, correct_answer]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_question'))

        # Save the new question in the database
        new_question = Question(
            question=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            answer=correct_answer
        )
        db.session.add(new_question)
        db.session.commit()

        flash('Question added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

    return render_template('add_question.html')

@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    question_list = [{
        "id": q.id,
        "question": q.question,
        "options": [q.option_a, q.option_b, q.option_c, q.option_d],
        "answer": q.answer  # Remove this if exposing answers is not intended
    } for q in questions]
    return {"questions": question_list}, 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
