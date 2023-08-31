# test_index_rendering.py
def test_index_page_rendering(client):
    response = client.get('/')
    assert response.status_code == 200, f"Failed to render index page. HTTP Status: {response.status_code}"
    assert b"<!DOCTYPE html>" in response.data, "HTML not found in the response"
