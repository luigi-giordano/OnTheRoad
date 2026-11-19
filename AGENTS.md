# AGENTS.md

## Regole di lavoro

- Prima di modificare, proponi un piano e aspetta conferma.
- Lavora su un branch dedicato alla sessione, mai direttamente su `main`.
- Tocca solo i file necessari al compito. Non modificare il README se non richiesto.
- Non riscrivere i test per farli passare: se un test fallisce, correggi il codice. Se un test è sbagliato, segnalalo.
- Non aggiungere dipendenze senza chiedere.
- Non leggere, stampare o committare il file `.env` né la cartella `.mcp-token/`.
- Alla fine dimmi cosa hai lanciato per verificare e cosa no.

## Il progetto

Assistente di viaggio AI per OnTheRoad (itinerari in moto, vendita di pacchetti know-how). Backend Python in `backend/`, frontend statico in `frontend/`.

### Come si lancia e si testa

- **Da `backend/`:** `python crea_db.py`, poi `python agente.py`.
- **Test:** da `backend/`, `python -m pytest -q tests`. Non serve la chiave né la rete: Trello e i modelli nei test sono finti.
- **Trello:** `python trello_mcp.py` fa il login OAuth (si apre il browser, una volta sola) e controlla board e lista. `python trello_mcp.py sincronizza` crea le card mancanti per le richieste salvate.
- **Misure:** la griglia è in `docs/domande.md`. Si misura con sessione nuova (cancellare `backend/sessioni.db`) e, per le richieste, con `backend/dati/richieste.db` cancellato. Ogni modifica all'agente si rimisura su tutta la griglia.

### File e responsabilità

- `config.py`: tutti i parametri. Niente valori scritti a mano nel codice.
- `modelli.py`: `Tappa`, `Itinerario` (validator: km e giorni coerenti con le tappe), `Richiesta`, `RispostaAgente`.
- `strumenti.py`: accesso ai dati (`esegui_select`, `cerca_nei_testi`, `carica_itinerario`, `salva_richiesta`, `PREZZI_PACCHETTI`).
- `agente.py`: agente, tool, ciclo di approvazione (`gestisci_approvazioni`), critico (`con_critico`), `main()` async.
- `documenti.py`: RAG sul corpus. `trello_mcp.py`: server MCP di Trello e card. `critico.py`: controllo dei numeri.
- `aikit/`: toolkit del corso. Non modificarlo.

### Cosa non toccare

- **Fonte dei dati:** `backend/dati/itinerari.json`. `itinerari.db` si rigenera con `crea_db.py`, non si modifica a mano. Le tappe sono la fonte di verità per km e giorni.
- **Sicurezza di `query_db`:** sola lettura (`mode=ro`), solo SELECT/WITH, una istruzione, limite righe. Non indebolirla.
- **Scrittura:** l'unica funzione che scrive è `salva_richiesta()`, su `richieste.db`, e solo dopo l'approvazione dell'operatore. `registra_richiesta` deve restare con `needs_approval=True`.
- **Prezzi:** li decide il codice (`PREZZI_PACCHETTI`), mai il modello.
- **Card Trello:** le crea il codice dopo il salvataggio, con il controllo di idempotenza (`#N`). Non dare al modello i tool di scrittura di Trello.
- **Istruzioni dell'agente:** niente risposte della griglia dentro `ISTRUZIONI` (rischio overfitting).
- **Frontend:** non modificarlo se il compito riguarda il backend. Fino a M5 `SAMPLE_ITINERARIES` in `frontend/app.js` deve restare identico a `itinerari.json`: se cambi un dato, cambialo in tutti e due.
- **Prezzi:** i pacchetti hanno prezzi fissi, uguali per tutti gli itinerari. Gli itinerari non hanno un prezzo.

I testi per l'utente sono in italiano.
