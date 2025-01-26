"""
app.py
The main entry point for the Flask app.
It contains routes, views and logic for handling
user authentication, quiz management and the admin dashboard.

Key Features:
- User authentication (login, logout, registration).
- Admin dashboard for managing users and questions.
- Quiz functionality including starting a quiz, answering questions, and viewing results.
- API endpoint for retrieving quiz questions.

Routes:
- `/` (Homepage)
- `/login` (User login)
- `/register` (User registration)
- `/logout` (User logout)
- `/quiz` (Start quiz)
- `/question/<question_number>` (Answer quiz questions)
- `/submit_quiz` (Submit quiz results)
- `/result` (View quiz results)
- `/admin` (Admin dashboard)
- `/make_admin/<user_id>` (Promote users to admins)
- `/delete_user/<user_id>` (Deletes a user)
- `/edit_question/<question_id>` (Edits an existing question)
- `/delete_question/<question_id>` (Deletes an existing question)
- `/add_question` (Add a new question - Admin only)
- `/api/questions` (Retrieve questions via API)
"""
from flask import abort, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from model import app, db, User, Question, QuizResult
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


# Setting up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def admin_required(f):
    """
    A decorator to restrict access to routes to admin-only routes.
    Args:
        f (function): The route function to decorate.

    Returns:
        function: The decoratedd function that checks if current user is an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """
    Renders the admin dashboard with all users and questions.
    Returns:
       str: Rendered HTML page for the dashboard.
    """
    users = User.query.all()
    questions = Question.query.all()
    return render_template('admin.html', users=users, questions=questions)


@app.route('/make_admin/<int:user_id>')
@login_required
@admin_required
def make_admin(user_id):
    """
    Promotes a user to be an admin.
    Args:
       user_id (int): The ID of the user to be promoted.

    Returns:
        Redirect: Rediecs to the admin dashboard
    """
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f"{user.username} is now an admin.", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    """
    Deletes a user and their quiz results.
    Args:
        user_id (int): The ID of the user to be deleted.

    Returns:
        Redirect: Redirects to teh admin dashboard.
    """
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
    """
    Edits an existing question.
    Args:
        question_id (int): The ID of the question to be edited.

    Returns:
        str: Rendered HTML page to edit the question.
        Redirect: Redirects to the admin dashboard after updating the question
    """
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
    """
    Deletes an existing quiz question.
    Args:
        question_id (int): The ID of the question to be deleted.

    Returns:
        Redirect: Redirects to the admin dashboard.
    """
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))


@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user by their ID for Flask-Login.

    Args:
        user_id (int): The ID of the user to be loaded.

    Returns:
        User: The user object associated with the given ID.
    """
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """
    Renders the home page.
    Returns:
        str: Rendered HTML page for the index page.
    """
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registeration. The first user is automatically admin.
    Returns:
        str: Rendered HTML page for registration.
        Redirect: Redirects to the login apon successfull rgistration.
    """
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handes user login. Redirects admins to the adin dashboard.
    Returns:
    str:
        Rendered HTML page for login.
        Redirect: Redirects to the admin dashboard or quiz page upon successful login.
    """
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


@app.route('/logout')
@login_required
def logout():
    """
    Handes user logout.
    Returns:
        Redirect: Redirects to the index page.

    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/quiz', methods=["GET", "POST"])
@login_required
def quiz():
    """
    Starts the quize session when the form is submitted.
    Returns:
        str: Rendered HTML page of the quiz.
        Redirect: Redircts to the first question upon starting the quiz.
    """
    if request.method == "POST":
        session['score'] = 0
        session['questions_answered'] = 0

        # Redirect to the quiz questions
        return redirect(url_for('next_question', question_number=1))
    questions = Question.query.all()
    session['total_questions'] = len(questions)
    return render_template('quiz.html', questions=questions)


@app.route('/question/<int:question_number>', methods=["GET", "POST"])
@login_required
def next_question(question_number):
    """
    Renders the current question in the quiz and handles user answers.
    Args:
        question_number (int): The number of the questions to display.

    Returns:
        str: Rendered HTML page for the question.
        Redirect: Redirects to the next question or the results page if quiz ends.
    """
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


@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    """
    Handes the submission of the quiz and stores the results in the db.
    Returns:
        Redirect: Redirects to the quiz results page.
    """
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


@app.route('/result')
@login_required
def result():
    """
    Display the suer's quiz resuts and the leaderboard.
    Returns:
        str: Rendered HTML page for the quiz results.
    """
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


@app.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    """
    Adds new questions to the quiz.

    Returns:
        str: Rendered HTML page for adding questions.
        Redirect: Redirects to the admin dashboard upon successful addition.
    """
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Capture form data for multiple questions
        question_data = []
        question_count = len(request.form) // 6

        for i in range(question_count):
            question_text = request.form.get(f'question_{i}')
            option_a = request.form.get(f'option_a_{i}')
            option_b = request.form.get(f'option_b_{i}')
            option_c = request.form.get(f'option_c_{i}')
            option_d = request.form.get(f'option_d_{i}')
            correct_answer = request.form.get(f'answer_{i}')

            # Validate each question's data
            if not all([
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer
            ]):
                flash('All fields are required for each question.', 'danger')
                return redirect(url_for('add_question'))

            question_data.append({
                'question': question_text,
                'option_a': option_a,
                'option_b': option_b,
                'option_c': option_c,
                'option_d': option_d,
                'answer': correct_answer
            })

        # Save the new questions to the database
        for data in question_data:
            new_question = Question(
                question=data['question'],
                option_a=data['option_a'],
                option_b=data['option_b'],
                option_c=data['option_c'],
                option_d=data['option_d'],
                answer=data['answer']
            )
            db.session.add(new_question)
        db.session.commit()

        flash('Questions added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect to dashboard

    return render_template('add_question.html')


@app.route('/api/questions', methods=['GET'])
def get_questions():
    """
    Provide an API endpoint to retrieve all quiz questions.
    Returns:
        dict: JSON response containing a list of all questions & their details.
    """
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
