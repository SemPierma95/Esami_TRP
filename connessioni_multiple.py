import requests
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
from tqdm import tqdm
import json
from threading import Lock
from time import sleep


# Variabile globale per tracciare il numero di thread terminati
threads_completed = 0
completion_lock = Lock()


bold_yellow = "\033[1m\033[93m"
reset = "\033[0m"

# Funzione per ottenere il numero totale di domande


def get_total_questions():
    response = requests.get(
        "https://srobodao.pythonanywhere.com/get_all_questions")
    if response.status_code == 200:
        questions_db = response.json()
        return len(questions_db)
    else:
        return 0


# Insieme per tracciare le sessioni completate
completed_sessions = set()

# Coda per tracciare la progressione di ciascuna sessione
progress_queue = Queue()

# Variabile per segnalare la fine del processo
done = threading.Event()

# Dizionario per mantenere le barre di avanzamento per ciascuna sessione
pbar_dict = {}

# Funzione per aggiornare la barra di avanzamento


def update_progress_bar():
    total_questions_read = 0
    while not done.is_set():
        try:
            session_data = progress_queue.get(timeout=1)
        except Queue.Empty:
            continue

        session_id = session_data[0]
        current = session_data[1]
                
        # Verifica se la sessione è già stata completata
        if session_id in completed_sessions:
            continue  # Ignora gli aggiornamenti per sessioni completate

        # Controlla se la sessione è stata completata
        if current == "COMPLETATO":
            if session_id in pbar_dict:
                pbar = pbar_dict.pop(session_id, None)
                if pbar:
                    pbar.n = pbar.total  # Imposta manualmente il conteggio al totale
                    pbar.last_print_n = pbar.total
                    pbar.close()
                completed_sessions.add(session_id)
            continue

        # Altrimenti, procedi come prima
        total = session_data[2]
        if session_id not in pbar_dict:
            pbar_dict[session_id] = tqdm(total=total, desc=f"{bold_yellow}Session {session_id}{reset}", unit="domande", dynamic_ncols=True,
                                         bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} questions [elapsed: {elapsed} remaining: {remaining}]", colour="green")

        pbar = pbar_dict[session_id]
        pbar.total = total  # Aggiorna il totale nel caso sia cambiato
        pbar.n = current
        pbar.last_print_n = current
        pbar.update()
        total_questions_read += current

    # Forza una nuova riga prima di stampare il totale
    print("\nTotale delle domande lette:", total_questions_read)


# Funzione per simulare una sessione utente
def simulate_user_session(total_questions):
    with requests.Session() as session:
        fetch_all_questions(session, total_questions)


def fetch_all_questions(session, total_questions):
    current_question_count = 0
    session_id = id(session)
    session_completed = False  
    
    while True:
        sleep(0.1)
        response = session.get("https://srobodao.pythonanywhere.com/get_question")
        
        # Aggiunto qui il controllo per il codice di stato 204
        if response.status_code == 204 and not session_completed:
            print(f"\nSessione {session_id} completata! - ricevuto codice di stato 204, segnalo COMPLETATO")
            # Segnala che la sessione è completa
            progress_queue.put((session_id, "COMPLETATO"))
            # Incrementa il conteggio dei thread completati in modo thread-safe
            with completion_lock:
                global threads_completed
                threads_completed += 1
            session_completed = True
            break
        
        if response.status_code == 200:
            print(f"\nSessione {session_id} - ricevuto codice di stato 200, aggiorno la barra di avanzamento")
            data = response.json()
            
            if "message" in data and not session_completed:
                # Questa parte potrebbe non essere più necessaria, ma la lascio per completezza
                progress_queue.put((session_id, "COMPLETATO"))
                session_completed = True
                break
            
            question = data.get("question")
            if question:
                current_question_count += 1
                progress_queue.put((session_id, current_question_count, total_questions))

                
def check_for_repeated_questions():
    all_questions = set()  # Set per tenere traccia di tutte le domande ricevute
    repeated_questions = {}  # Dizionario per tracciare domande ripetute per ciascuna sessione
    print("\nControllo delle domande ripetute...")
    print(threads_completed, "sessioni completate")
    print(numero_di_sessioni, "sessioni simulate")

    while threads_completed < numero_di_sessioni or not done.is_set():
        try:
            session_data = progress_queue.get(timeout=1)
        except Queue.Empty:
            continue

        session_id = session_data[0]
        current = session_data[1]

        if session_id == "COMPLETATO":
            continue  # Ignora gli aggiornamenti di completamento della sessione

        question = session_data[3]  # Aggiungi questa riga per ottenere la domanda

        # Controllo per domande ripetute
        if question in all_questions:
            if session_id not in repeated_questions:
                repeated_questions[session_id] = set()
            repeated_questions[session_id].add(question)

        all_questions.add(question)

    # Dopo che tutte le sessioni sono state elaborate, stampa le domande ripetute per ciascuna sessione
    for session_id, repeated in repeated_questions.items():
        if repeated:
            print(f"Sessione {session_id}: Domande ripetute -> {', '.join(repeated)}")
        else:
            print(f"Sessione {session_id}: Nessuna domanda ripetuta")

# Ottieni il numero totale di domande
total_questions = get_total_questions()
print("Numero totale di domande:", total_questions)

numero_di_sessioni= 3

# Usa ThreadPoolExecutor per effettuare due sessioni in parallelo
with ThreadPoolExecutor(max_workers=numero_di_sessioni+1) as executor:  # 5 sessioni utente + 1 per la barra di avanzamento
    executor.submit(update_progress_bar)
    for _ in range(numero_di_sessioni):  # 5 sessioni utente
        executor.submit(simulate_user_session, total_questions)

# Questa parte assicura che done.set() venga chiamato solo quando tutti i thread sono completati
executor.shutdown()
done.set()
sleep(2)

# Stampa i messaggi delle sessioni completate
print("\nSessioni completate:")
for session_id in completed_sessions:
    print(f"Sessione {session_id} completata!")

