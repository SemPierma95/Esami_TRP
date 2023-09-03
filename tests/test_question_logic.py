import json
import os
import shutil
import pytest
from app import app

# Creare una fixture per il client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test per la logica di ottenimento delle domande
def test_get_question_logic(client):
    # Step 1: Creare una copia temporanea di questions.json
    shutil.copy('questions.json', 'temp_questions.json')

    # Step 2 e 3: Eseguire un ciclo che simula l'ottenimento di tutte le domande fino all'esaurimento
    with open('temp_questions.json', 'r') as f:
        questions_db = json.load(f)
    total_questions = len(questions_db)
    
    for _ in range(total_questions):
        response = client.get('/get_question')
        assert 'message' not in response.get_json(), "Le domande non dovrebbero essere ancora finite"
    
    response = client.get('/get_question')
    assert response.get_json()['message'] == "Le domande sono finite, ricominciamo."

    # Step 4 e 5: Reset della sessione e verifica che il ciclo possa ricominciare
    with client.session_transaction() as session:
        session.clear()
    
    response = client.get('/get_question')
    assert 'message' not in response.get_json(), "Dovrebbe essere possibile ottenere una nuova domanda"

    # Step 6: Cancellare il file temporaneo di questions.json
    os.remove('temp_questions.json')
