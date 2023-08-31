import sys
sys.path.append('/mnt/c/Users/paolo/Documents/Progetti di coding/University_Test')

# conftest.py
import pytest
from app import app  # Importa l'app Flask dal tuo file app.py

@pytest.fixture
def client():
    app.config['TESTING'] = True  # Abilita la modalità di test
    with app.test_client() as client:  # Crea un client di test
        yield client  # Rende il client di test disponibile ai tuoi test cases
