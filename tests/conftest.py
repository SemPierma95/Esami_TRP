import os
import sys

# Ottieni la directory corrente del file di script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Risali alla directory root
root_directory = os.path.join(current_directory, '..')

# Aggiungi la root_directory al sys.path
sys.path.append(root_directory)


# conftest.py
import pytest
from app import app  # Importa l'app Flask dal tuo file app.py

@pytest.fixture
def client():
    app.config['TESTING'] = True  # Abilita la modalità di test
    with app.test_client() as client:  # Crea un client di test
        yield client  # Rende il client di test disponibile ai tuoi test cases
