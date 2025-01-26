"""
model.py

This module define the database models for the Flask app. It uses SQLAlchemy to represent the database structure.

Classes:
- `User`: Represents the user in the application.
- `QuizResult`: Stores results of quizzes taken by users.
- `Question`: Represents a quiz question.

Data configuration:
- The SQLite db is initialized using SQLAschemy and is located at database.db.
"""
from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# The flask app
app = Flask(__name__)

# Configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    """
    User in the application.
    Attributes;
       id (int): the suer's uniquew ID.
       username (str): The user's name.
       password (str): The user's hashed password.
       is_admin (bool): Is the user an admin.
       results (list): A list of quiz results associated with the user.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    results = db.relationship('QuizResult', backref='user', lazy=True)


class QuizResult(db.Model):
    """
    The user's quiz results.
    Attributes:
        id (int): The result's uniques ID.
        score (int): The score achieved in the quiz.
        total (int): The total number of questions in the quiz.
        user_id (int): The Id of the user who took the quiz.
        date (datetime): The date and time the quiz was taken.
    """
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Question(db.Model):
    """
    A question in the quiz.
    Attributes:
        id (int): The question's uniques ID.
        question (str): The text of the question.
        option_a (str): Option A.
        option_b (str): Option B.
        option_c (str): Option C.
        option_d (str): Option D.
        answer (str): The correct answer to the question.
    """
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        """
        The string representation of the question.
        Return:
            str: A string representation of the question.
        """
        return f'<Question {self.id} - {self.question}>'
