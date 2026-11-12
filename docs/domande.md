# Griglia di domande

Ogni modifica all'assistente si rimisura su tutta la griglia (regola anti-regressione, M3·L6).

| # | Domanda | Strada attesa | Risposta attesa |
|---|---|---|---|
| 1 | Quanti km è l'itinerario in Norvegia? | dati | 1.140 km |
| 2 | Quali itinerari sono di difficoltà Facile? | dati | Albania Loop, Corsica |
| 3 | Ho 7 giorni o meno: cosa posso fare? | dati | Dolomiti e Stelvio (7 giorni, 740 km), Corsica (7 giorni, 600 km) |
| 4 | Che documenti servono per i Balcani? | dati | carta verde per Bosnia e Montenegro, vignetta Slovenia, … |
| 5 | Cosa include il pacchetto Completo e quanto costa? | documenti | €89, elenco contenuti |
| 6 | Posso avere un rimborso sul pacchetto standard? | documenti | no, ma si può sostituire con un altro itinerario |
| 7 | Con una 300cc posso fare l'Albania? | documenti + dati | sì (FAQ), difficoltà Facile |
| 8 | Quanto costa la benzina in Giappone? | nessuna | rifiuto: non è nelle fonti |

## Problemi noti nei dati

- Km e giorni: corretti. Regola: le tappe sono la fonte di verità
  (km_totali = somma km tappe, giorni = notti + 1). Garantito da due test in test_db.py.
- Il frontend (SAMPLE_ITINERARIES in app.js) mostra ancora i vecchi valori:
  si allinea in M5, quando leggerà dall'API.
- Dolomiti e Stelvio: la tappa Stelvio → Aosta dichiara 220 km, su strada
  sono probabilmente oltre 350. Il riassunto cita l'Austria ma nessuna tappa è lì.

## Misure

| Data | Versione | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Totale |
|---|---|---|---|---|---|---|---|---|---|---|
| 10/11 | solo query_db | ✅ | ✅ | ✅ | ✅ | ⏸️ | ⏸️ | 🟡 | ✅ | 5/8 + 1 parziale |

| 10/11 | + RAG (22 chunk) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 | ✅ | 7/8 + 1 parziale |

| 10/11 | + docstring cerca_documenti (moto, cilindrata) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 | ✅ | 7/8 + 1 parziale — nessun effetto |

| 10/11 | + ISTRUZIONI: domande di consiglio su entrambe le fonti | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8/8 |