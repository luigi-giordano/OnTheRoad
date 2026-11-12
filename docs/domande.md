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

## Griglia estesa (domande 9-16)

Misurare con sessione nuova: cancellare `backend/sessioni.db` prima del giro
e fare le domande nell'ordine indicato.

### Follow-up con la sessione

| # | Domanda | Risposta attesa | Cosa misura |
|---|---------|-----------------|-------------|
| 9a | Quali itinerari sono di difficoltà Avanzata? | Norvegia (11 gg, 1.140 km, 109 €) e Turchia (11 gg, 1.590 km, 99 €) | — |
| 9b | E quale dei due costa meno? | Turchia, 99 € | risolve "dei due" dalla sessione |
| 10a | Parlami dell'itinerario in Corsica | 7 gg, 600 km, Facile, 49 €, Maggio – Ottobre | — |
| 10b | Che documenti servono? | Carta d'identità o passaporto, patente A, documento assicurativo moto | capisce che si parla ancora della Corsica |

### Nuova griglia domande Codici esatti (11-13) e confronti (14-16)

| # | Domanda | Risposta attesa | Cosa misura |
|---|---------|-----------------|-------------|
| 11 | Quale itinerario passa per la SH8? | Albania Loop, tappa Riviera Albanese — Himarë (tratto Saranda–Vlorë) | LIKE sulle note delle tappe |
| 12 | Su quale itinerario si percorre la D81? | Corsica: riassunto e tappa Porto e le Calanche (strada stretta, richiede attenzione) | codice in due campi diversi |
| 13 | Cosa dicono gli itinerari sull'autostrada A1? | Balcani: rientro a Zagabria via A1 croata (nota di tappa) e radar fissi sulla A1 in Montenegro (consigli). Non deve parlare dell'A1 italiana | stesso codice in due tabelle, nessuna invenzione |
| 14 | Qual è l'itinerario più lungo in km e quale il più corto? | Balcani 1.870 km; Corsica 600 km | ORDER BY / MAX-MIN |
| 15 | Qual è la tappa più lunga di tutti gli itinerari? | Efeso (Selçuk), Turchia, 430 km (seconda: Zagabria, Balcani, 410) | query sulle tappe, non sugli itinerari |
| 16 | Quali itinerari prevedono un traghetto, anche opzionale? | Norvegia, Albania, Balcani, Corsica, Turchia (traversata in traghetto sul Bosforo, nella nota di Istanbul). "Barca" in mezzi_tappa da sola non basterebbe| cerca anche nelle note, non solo in mezzi_tappa. |

## Problemi noti nei dati

- Km e giorni: corretti. Regola: le tappe sono la fonte di verità
  (km_totali = somma km tappe, giorni = notti + 1). Garantito da due test in test_db.py.
- Il frontend (SAMPLE_ITINERARIES in app.js) mostra ancora i vecchi valori:
  si allinea in M5, quando leggerà dall'API.
- Dolomiti e Stelvio: la tappa Stelvio → Aosta dichiara 220 km, su strada
  sono probabilmente oltre 350. Il riassunto cita l'Austria ma nessuna tappa è lì.

## Misure

### Griglia 1-8

| Data | Versione | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Totale |
|---|---|---|---|---|---|---|---|---|---|---|
| 10/11 | solo query_db | ✅ | ✅ | ✅ | ✅ | ⏸️ | ⏸️ | 🟡 | ✅ | 5/8 + 1 parziale |
| 10/11 | + RAG (22 chunk) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 | ✅ | 7/8 + 1 parziale |
| 10/11 | + docstring cerca_documenti (moto, cilindrata) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 | ✅ | 7/8 + 1 parziale — nessun effetto |
| 10/11 | + ISTRUZIONI: domande di consiglio su entrambe le fonti | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8/8 |
| 12/11 | dati corretti: km e giorni dalle tappe | ✅ | — | ✅ | — | — | — | — | — | solo 1 e 3 verificate |
| 12/11 | + docstring query_db: campi di testo con LIKE | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8/8 |
| 12/11 | + tool cerca_testo (UNION ALL nel codice) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8/8 |

Osservazioni:

- 12/11, griglia 1-8 con cerca_testo: la 8 rifiuta correttamente ma dichiara
  di aver cercato anche nei dati delle tappe, mentre ha chiamato solo
  cerca_documenti. Da rivedere se si ripete.

- 12/11, domanda 16: in 1 prova su 3 la Turchia viene esclusa. cerca_testo
  restituisce la nota di Istanbul, ma il modello non considera la traversata
  sul Bosforo un traghetto dell'itinerario. Il recupero è corretto, l'ambiguità
  sta nella domanda: non si corregge con le ISTRUZIONI (rischio overfitting).

- Conclusione: una frase nella docstring non bastava a ottenere SQL complesso
  corretto (JOIN cartesiano, righe tagliate a 50). La ricerca nei testi è
  stata spostata nel codice (cerca_nei_testi in strumenti.py).

### Griglia estesa 9-16

| Data | Versione | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | Totale |
|---|---|---|---|---|---|---|---|---|---|---|
| 12/11 | baseline | ✅ | ✅ | ✅ | ✅ | 🟡 | ✅ | ✅ | ✅ | 7/8 + 1 parziale (13: manca la A1 in consigli) |
| 12/11 | + docstring query_db: campi di testo con LIKE | ✅ | ✅ | ✅ | ✅ | 🟡 | ✅ | ✅ | ❌ | 6/8 + 1 parziale — JOIN cartesiano (96 righe, taglio a 50) |
| 12/11 | + tool cerca_testo (UNION ALL nel codice) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8/8 — ripetizioni: 13 → 3/3, 16 → 2/3 |