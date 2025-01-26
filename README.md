# Flask Quiz Application

## Overview
A simple interactive web-based quiz application developed using Flask that allows users to register, login, take quizzes, and get their scores. This project includes functionalities for user authentication, dynamic quiz handling, and session management.

## Technologies used
- **Backend:** Python ([Flask](https://flask.palletsprojects.com/))
- **Frontend:** HTML, CSS, [Bootstrap](https://getbootstrap.com/)
- **Database:** SQLite ([Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/))

## Features
- User authentication (register, login, logout).
- Take MCQ quizzes and track your scores.
- Timer to each question to answer before it.
- Leaderboard that displays the top 5 users based on their quiz scores.
- Responsive UI built with Bootstrap
- Option for admins to add new quiz questions (protected route).

## Routes
- `/login` - Login page for registered users.
- `/register` - Registration page for new users.
- `/quiz` - Quiz homepage initiates the quiz session.
- `/question/<int:question_number>` - Handles rendering each quiz question dynamicall by its question number.
- `/result` - Displays the results after completing the quiz.

---

## Dependencies
The application depends on several Python packages to handle routing, database management, and user authentication. These include:
1. **Flask:** Framework for building web applications.
2. **Flask-Login:** Adds user session management and authentication support.
3. **Flask-SQLAlchemy:** Provide a simple interface for working with databases.
4. **Werkzeug:**  A WSGI utility library used by Flask.
All the dependencies are listed in the `requirements.txt` file.

---

## Installation
1. Clone this repo:
   ```bash
   git clone https://github.com/NafisaKaruri/flask_quiz_app
   cd flask_quiz_app
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open the browser and go to:
   ```
   https://127.0.0.1:5000
   ```

---

## Project Architecture
The application follows the **Model-View-Control (MVC)** pattern.

---

## Contributing
Pull requests are more than welcomed! For major changes please open an issue first to discuss what you would like to change.

---

### License
This project is open-source. Feel free to use if for educational purposes.
