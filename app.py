from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import random
import json
import os

app = Flask(__name__)

# Carica il database delle domande all'avvio dell'applicazione
try:
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)
except FileNotFoundError:
    questions_db = []
    
def format_path(filename):
    image_path = os.path.join('static', 'uploads', filename)
    return image_path.replace("\\", "/")

# Endpoint per ottenere una domanda casuale
@app.route('/get_question', methods=['GET'])
def get_question():
    # Ricarica il database delle domande
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)

    question = random.choice(questions_db)
    return jsonify(question)

# Endpoint per aggiungere una nuova domanda
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
    new_entry = {
        'question': new_question,
        'hints': new_hints
    }

    if image_file:
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join('static/uploads', filename))
        
        # Formatta il percorso dell'immagine
        image_path = format_path(os.path.join('static/uploads', filename))
        new_entry['image'] = image_path

    questions_db.append(new_entry)
    
    with open('questions.json', 'w') as f:
        json.dump(questions_db, f)

    return jsonify(new_entry), 201

# Funzione per formattare il percorso del file
def format_path(filepath):
    return filepath.replace("\\", "/")


# Endpoint per la pagina principale
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Endpoint per il favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
