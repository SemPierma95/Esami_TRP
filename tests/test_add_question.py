import json
from io import BytesIO
from werkzeug.datastructures import FileStorage

def test_add_question(client):
    # Dati della nuova domanda da aggiungere
    new_question_data = {
        "newQuestion": "What is 2+2?",
        "newHints": "It's not 3, It's not 5"
    }

    # Creazione di un oggetto FileStorage fittizio
    fake_file = FileStorage(
        stream=BytesIO(b"fake file content"),  # I contenuti del file come byte
        filename="fake_image.jpg",  # Il nome del file
        content_type="image/jpeg"  # Il tipo di contenuto (MIME type)
    )

    # Verifica che la nuova domanda venga aggiunta correttamente e che il server restituisca un codice di stato HTTP 201
    response = client.post('/add_question', data={
        **new_question_data,
        "newImage": fake_file
    })
    assert response.status_code == 201
    assert json.loads(response.data.decode('utf-8'))["question"] == "What is 2+2?"

    # Carica il file questions.json per verificare che la nuova domanda sia stata effettivamente aggiunta
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)
    assert any(q['question'] == "What is 2+2?" for q in questions_db)

    # Rimuovi la domanda aggiunta per mantenere il database pulito
    questions_db = [q for q in questions_db if q['question'] != "What is 2+2?"]
    with open('questions.json', 'w') as f:
        json.dump(questions_db, f)

    # Verifica che la domanda sia stata effettivamente rimossa
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)
    assert not any(q['question'] == "What is 2+2?" for q in questions_db)
