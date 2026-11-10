# Griglia di domande

Ogni modifica all'assistente si rimisura su tutta la griglia (regola anti-regressione, M3·L6).

| # | Domanda | Strada attesa | Risposta attesa |
|---|---|---|---|
| 1 | Quanti km è l'itinerario in Norvegia? | dati | 3.100 km |
| 2 | Quali itinerari sono di difficoltà Facile? | dati | Albania Loop, Corsica |
| 3 | Ho 7 giorni o meno: cosa posso fare? | dati | Dolomiti e Stelvio (7), Corsica (6) |
| 4 | Che documenti servono per i Balcani? | dati | carta verde per Bosnia e Montenegro, vignetta Slovenia, … |
| 5 | Cosa include il pacchetto Completo e quanto costa? | documenti | €89, elenco contenuti |
| 6 | Posso avere un rimborso sul pacchetto standard? | documenti | no, ma si può sostituire con un altro itinerario |
| 7 | Con una 300cc posso fare l'Albania? | documenti + dati | sì (FAQ), difficoltà Facile |
| 8 | Quanto costa la benzina in Giappone? | nessuna | rifiuto: non è nelle fonti |

## Problemi noti nei dati

I km totali di ogni itinerario non coincidono con la somma dei km delle tappe (es. Norvegia: 3.100 km dichiarati, 1.140 sommando le tappe). Anche giorni e notti non tornano sempre. Va deciso quale valore è giusto prima di misurare, altrimenti l'assistente darà risposte diverse a seconda della query che scrive.

## Misure

| Data | Versione | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Totale |
|---|---|---|---|---|---|---|---|---|---|---|
| 10/11 | solo query_db | ✅ | ✅ | ✅ | ✅ | ⏸️ | ⏸️ | 🟡 | ✅ | 5/8 + 1 parziale |