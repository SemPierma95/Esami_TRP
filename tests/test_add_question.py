# test_add_question.py
import json

def test_add_question(client):
    # Dati della nuova domanda da aggiungere
    new_question = {"question": "What is 2+2?", "answer": "4"}

    # Verifica che la nuova domanda venga aggiunta correttamente e che il server restituisca un codice di stato HTTP 201
    response = client.post('/add_question', json=new_question)
    assert response.status_code == 201
    assert response.data.decode('utf-8') == 'Domanda aggiunta'

    # Carica il file questions.json per verificare che la nuova domanda sia stata effettivamente aggiunta
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)
    assert new_question in questions_db

    # Rimuovi la domanda aggiunta per mantenere il database pulito
    questions_db.remove(new_question)
    with open('questions.json', 'w') as f:
        json.dump(questions_db, f)

    # Verifica che la domanda sia stata effettivamente rimossa
    with open('questions.json', 'r') as f:
        questions_db = json.load(f)
    assert new_question not in questions_db
