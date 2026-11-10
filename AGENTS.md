# AGENTS.md

## Regole di lavoro

- Prima di modificare, proponi un piano e aspetta conferma.
- Lavora su un branch dedicato alla sessione, mai direttamente su `main`.
- Tocca solo i file necessari al compito. Non modificare il README se non richiesto.
- Non riscrivere i test per farli passare: se un test fallisce, correggi il codice. Se un test è sbagliato, segnalalo.
- Non aggiungere dipendenze senza chiedere.
- Non leggere, stampare o committare il file `.env`.
- Alla fine dimmi cosa hai lanciato per verificare e cosa no.

## Il progetto

Assistente di viaggio AI per OnTheRoad (itinerari in moto). Backend Python in `backend/`, frontend statico in `frontend/`.

- **Come si lancia:** da `backend/`, `python crea_db.py` e poi `python agente.py`.
- **Come si testa:** da `backend/`, `python -m pytest -q tests` (non serve la chiave).
- **Fonte dei dati:** `backend/dati/itinerari.json`. Il file `itinerari.db` si rigenera, non si modifica a mano.
- **Parametri:** tutti in `backend/config.py`. Niente valori scritti a mano nel codice.
- **Sicurezza di `query_db`:** sola lettura, solo SELECT, limite righe. Non indebolirla.
- **Frontend:** non modificarlo se il compito riguarda il backend.
- I testi per l'utente sono in italiano.
