from flask import Flask, request, jsonify, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
import random
import json
import os

app = Flask(__name__)

app.secret_key = 'paolo'


# Carica il database delle domande all'avvio dell'applicazione
try:
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)
except FileNotFoundError:
    questions_db = []


def format_path(filename):
    if "static/uploads" not in filename:
        image_path = os.path.join('static', 'uploads', filename)
    else:
        image_path = filename

    return image_path.replace("\\", "/")





# Variabile globale per tenere traccia delle domande non utilizzate
unused_questions = []

# Endpoint per ottenere una domanda casuale


@app.route('/get_question', methods=['GET'])
def get_question():
    if 'unused_questions' not in session:
        with open('questions.json', 'r') as f:
            questions_db = json.load(f)
        session['unused_questions'] = questions_db.copy()

    unused_questions = session['unused_questions']

    if not unused_questions:
        session['unused_questions'] = questions_db.copy()
        return jsonify({"message": "Le domande sono finite, ricominciamo."})

    question = random.choice(unused_questions)
    unused_questions.remove(question)
    session['unused_questions'] = unused_questions

    return jsonify(question)


@app.route('/add_question', methods=['POST'])
def add_question():
    new_question = request.form.get('newQuestion')
    new_hints = request.form.get('newHints')

    # Controllo se new_hints è None
    if new_hints is not None:
        new_hints = new_hints.split(", ")
    else:
        new_hints = []

    image_file = request.files.get('newImage')

    # Trova l'ID massimo tra le domande esistenti
    max_id = max([q.get('id', 0) for q in questions_db])

    new_entry = {
        'id': max_id + 1,  # Assegna l'ID successivo
        'question': new_question,
        'hints': new_hints
    }

    if image_file:
        filename = secure_filename(image_file.filename)
        if not os.path.exists('static/uploads'):
            os.makedirs('static/uploads')
        image_file.save(os.path.join('static/uploads', filename))

        # Formatta il percorso dell'immagine
        image_path = format_path(os.path.join('static/uploads', filename))
        new_entry['image'] = image_path

    questions_db.append(new_entry)

    with open('questions.json', 'w') as f:
        json.dump(questions_db, f, indent=4)

    return jsonify(new_entry), 201

# funzione per mostrare tutte le domande


@app.route('/get_all_questions', methods=['GET'])
def get_all_questions():
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)
    return jsonify(questions_db)

@app.route('/update_question/<int:question_id>', methods=['POST'])
def update_question(question_id):
    edited_question = request.form.get('question')
    edited_hints = request.form.get('hints')
    
    if edited_hints:
        edited_hints = edited_hints.split(", ")
    else:
        edited_hints = []

    image_file = request.files.get('newImage')
    delete_image = request.form.get('deleteImage')  # Aggiunto

    for question in questions_db:
        if question['id'] == question_id:
            if edited_question:
                question['question'] = edited_question
            if edited_hints:
                question['hints'] = edited_hints

            if image_file:
                filename = secure_filename(image_file.filename)
                if not os.path.exists('static/uploads'):
                    os.makedirs('static/uploads')
                image_file.save(os.path.join('static/uploads', filename))
                image_path = format_path(filename)  # Usare solo il nome del file
                question['image'] = image_path
            elif delete_image:  # Aggiunto
                question.pop('image', None)  # Aggiunto

            with open('questions.json', 'w') as f:
                json.dump(questions_db, f, indent=4)

            return jsonify({"message": "Domanda aggiornata con successo", "status":200}), 200

    return jsonify({"message": "Domanda non trovata", "status": 404}), 404



# Funzione per eliminare una domanda


@app.route('/delete_question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    for question in questions_db:
        if question['id'] == question_id:
            questions_db.remove(question)
            with open('questions.json', 'w') as f:
                json.dump(questions_db, f, indent=4)
            return jsonify({"message": "Domanda eliminata con successo"}), 200
    return jsonify({"message": "Domanda non trovata"}), 404


# Endpoint per la pagina principale
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Endpoint per il favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/edit_questions', methods=['GET'])
def edit_questions():
    return render_template('edit_questions.html')



if __name__ == '__main__':
    app.run(debug=True)
