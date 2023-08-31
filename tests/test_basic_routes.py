# test_basic_routes.py
def test_index_page(client):
    # Verifica che la rotta principale "/" sia accessibile e restituisca un codice di stato HTTP 200
    response = client.get('/')
    assert response.status_code == 200

def test_favicon(client):
    # Verifica che la favicon sia accessibile e restituisca un codice di stato HTTP 200
    response = client.get('/favicon.ico')
    assert response.status_code == 200
