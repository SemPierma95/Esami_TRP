from flask import Flask, request, jsonify, render_template, session, send_from_directory
from flask_session import Session  # estensione di sessione per Flask
import random
import json
import os

app = Flask(__name__)
app.secret_key = 'yourSecretKey'  # per la sessione
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

try:
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)
except FileNotFoundError:
    questions_db = []

@app.route('/get_question', methods=['GET'])
def get_question():
    if 'used_questions' not in session:
        session['used_questions'] = []
        session['unused_questions'] = questions_db.copy()

    if not session['unused_questions']:
        session['unused_questions'] = questions_db.copy()
        session['used_questions'] = []

    question = random.choice(session['unused_questions'])
    session['used_questions'].append(question)
    session['unused_questions'].remove(question)

    return jsonify(question)

@app.route('/add_question', methods=['POST'])
def add_question():
    new_question = request.json
    questions_db.append(new_question)
    with open('questions.json', 'w') as f:
        json.dump(questions_db, f)
    return 'Domanda aggiunta', 201

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)
