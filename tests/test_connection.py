# test_connection.py
def test_get_question_connection(client):
    # Verifica che la chiamata HTTP alla rotta /get_question ritorni uno stato HTTP 200 (OK)
    response = client.get('/get_question')
    assert response.status_code == 200

