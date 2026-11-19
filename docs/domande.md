# Griglia di domande

Ogni modifica all'assistente si rimisura su tutta la griglia (regola anti-regressione).

| #   | Domanda                                            | Strada attesa    | Risposta attesa                                           |
| --- | -------------------------------------------------- | ---------------- | --------------------------------------------------------- |
| 1   | Quanti km è l'itinerario in Norvegia?              | dati             | 1.140 km                                                  |
| 2   | Quali itinerari sono di difficoltà Facile?         | dati             | Albania Loop, Corsica                                     |
| 3   | Ho 7 giorni o meno: cosa posso fare?               | dati             | Corsica (7 giorni, 600 km)                                |
| 4   | Che documenti servono per i Balcani?               | dati             | carta verde per Bosnia e Montenegro, vignetta Slovenia, … |
| 5   | Cosa include il pacchetto Completo e quanto costa? | documenti        | €89, elenco contenuti                                     |
| 6   | Posso avere un rimborso sul pacchetto standard?    | documenti        | no, ma si può sostituire con un altro itinerario          |
| 7   | Con una 300cc posso fare l'Albania?                | documenti + dati | sì (FAQ), difficoltà Facile                               |
| 8   | Quanto costa la benzina in Giappone?               | nessuna          | rifiuto: non è nelle fonti                                |

## Griglia estesa (domande 9-16)

Misurare con sessione nuova: cancellare `backend/sessioni.db` prima del giro
e fare le domande nell'ordine indicato.

### Follow-up con la sessione

| #   | Domanda                                      | Risposta attesa                                                       | Cosa misura                               |
| --- | -------------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------- |
| 9a  | Quali itinerari sono di difficoltà Avanzata? | Norvegia (11 gg, 1.140 km) e Turchia (11 gg, 1.590 km)                | —                                         |
| 9b  | E quale dei due è più lungo?                 | Turchia, 1.590 km                                                     | risolve "dei due" dalla sessione          |
| 10a | Parlami dell'itinerario in Corsica           | 7 gg, 600 km, Facile, Maggio – Ottobre                                | —                                         |
| 10b | Che documenti servono?                       | Carta d'identità o passaporto, patente A, documento assicurativo moto | capisce che si parla ancora della Corsica |

### Nuova griglia domande Codici esatti (11-13) e confronti (14-16)
                                    |
| 11  | Quale itinerario passa per la SH8?                        | Albania Loop, tappa Riviera Albanese — Himarë (tratto Saranda–Vlorë)                                                                                                                      | LIKE sulle note delle tappe                      |
| 12  | Su quale itinerario si percorre la D81?                   | Corsica: riassunto e tappa Porto e le Calanche (strada stretta, richiede attenzione)                                                                                                      | codice in due campi diversi                      |
| 13  | Cosa dicono gli itinerari sull'autostrada A1?             | Balcani: rientro a Zagabria via A1 croata (nota di tappa) e radar fissi sulla A1 in Montenegro (consigli). Non deve parlare dell'A1 italiana                                              | stesso codice in due tabelle, nessuna invenzione |
| 14  | Qual è l'itinerario più lungo in km e quale il più corto? | Balcani 1.870 km; Corsica 600 km                                                                                                                                                          | ORDER BY / MAX-MIN                               |
| 15  | Qual è la tappa più lunga di tutti gli itinerari?         | Efeso (Selçuk), Turchia, 430 km (seconda: Zagabria, Balcani, 410)                                                                                                                         | query sulle tappe, non sugli itinerari           |
| 16  | Quali itinerari prevedono un traghetto, anche opzionale?  | Norvegia, Albania, Balcani, Corsica. Turchia accettabile ma non richiesta (traversata del Bosforo a Istanbul: gita, non mezzo del viaggio). "Barca" in mezzi_tappa da sola non basterebbe | cerca anche nelle note, non solo in mezzi_tappa  |

## Griglia richieste (domande 17-20)

Misurare con sessione nuova e `backend/dati/richieste.db` cancellato. Dopo il giro,
le richieste salvate devono essere esattamente quelle approvate.
Tracce: `[approvazione]`, `[rifiutata]`, `[rifiutata dal codice]`, `[richiesta] n. X salvata`.

| #   | Domanda                                                                   | Comportamento atteso                                                                                   |
| --- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 17a | Vorrei il pacchetto Completo per la Corsica                               | chiede nome ed email; nessuna proposta di registrazione                                                |
| 17b | Mario Rossi, mario.rossi@example.com, prima metà di giugno                | propone la richiesta (corsica, Completo) → approvazione → salvata; conferma numero e €89               |
| 18  | Prenota il Su misura per i Balcani: Anna Bianchi, anna@example            | email non valida: rifiutata dal codice, chiede di correggerla; nessuna richiesta salvata               |
| 19  | Voglio l'Essenziale per l'Albania, Luca Verdi, luca.verdi@example.com     | proposta → rifiuto con motivo "conferma prima il prezzo all'utente" → non salva, chiede conferma (€39) |
| 20  | Vorrei il pacchetto Completo per il Giappone, Sara Neri, sara@example.com | itinerario inesistente: lo dice e propone quelli disponibili; nessuna richiesta salvata                |

## Griglia Trello (domande 21-23)

Board "Richieste OnTheRoad" vuota, `richieste.db` cancellato, sessione nuova.
Tracce: `[trello] card creata`, `[trello] card già presente`, `[trello] card non creata`.

| #   | Prova                                            | Comportamento atteso                                                               |
| --- | ------------------------------------------------ | ---------------------------------------------------------------------------------- |
| 21  | 17a + 17b, approvata con `s`                     | card `#1 · Corsica — L'Isola Selvaggia · Completo · Mario Rossi` nella lista Nuove |
| 22  | dopo il giro: `python trello_mcp.py sincronizza` | `n. 1: card già presente`; sulla board resta una sola card #1                      |
| 23  | 19 rifiutata con motivo                          | nessuna card nuova                                                                 |

## Griglia trappola (domande 24-28): numeri da non inventare

Misurare due volte, con `CONFIG["critico"] = False` e `True`, sessione nuova ogni volta.

| #   | Domanda                                                                           | Risposta attesa                                                    | Trappola                            |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------- |
| 24  | Quanto spendo in tutto per il Completo della Corsica e l'Essenziale dell'Albania? | €128 (89 + 39)                                                     | calcolo: il critico deve approvarlo |
| 25  | Quanto costa il pacchetto Su misura per i Balcani?                                | €249 (prezzo fisso, uguale per tutti gli itinerari)                | confondere i due prezzi             |
| 26  | Quanti km al giorno in media si fanno in Norvegia?                                | circa 104 km (1.140 / 11)                                          | calcolo a mente                     |
| 27  | Quanto costa il traghetto per la Corsica?                                         | prezzo non nelle fonti; può dire durate (Livorno 5-6h, Genova 10h) | inventare un prezzo                 |
| 28  | Quanti km e quante ore di guida ha la tappa più lunga dei Balcani?                | Zagabria (rientro): 410 km, 5h 30m                                 | —                                   |

## Problemi noti nei dati

Risolti il 19/11:

- Km e giorni: le tappe sono la fonte di verità (km_totali = somma km tappe,
  giorni = notti + 1). Garantito dal validator di Itinerario e da due test in test_db.py.
- Frontend allineato: SAMPLE_ITINERARIES in app.js è identico a itinerari.json.
- Prezzi: tolto il price dell'itinerario. Si vendono solo pacchetti a prezzo fisso
  (Essenziale 39 €, Completo 89 €, Su misura 249 €), uguali per tutti gli itinerari.
- Dolomiti: la tappa Stelvio → Aosta (220 km) è stata divisa in Lago di Como — Varenna
  (150 km) e Aosta (230 km): 900 km in 8 giorni. Km e ore delle due tappe sono stime.
- Dolomiti: paese "Italia" (prima "Italia / Austria", senza tappe in Austria).

Aperti:

- Il frontend salva account e password in chiaro in localStorage (solo demo, segnalato
  nelle pagine di login e registrazione). Si risolve in M5 con il login sul backend.

## Misure

### Griglia 1-8

| Data  | Versione                                                | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | Totale                                                                                                |
| ----- | ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------------------------------------------------------------- |
| 10/11 | solo query_db                                           | ✅   | ✅   | ✅   | ✅   | ⏸️   | ⏸️   | 🟡   | ✅   | 5/8 + 1 parziale                                                                                      |
| 10/11 | + RAG (22 chunk)                                        | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 🟡   | ✅   | 7/8 + 1 parziale                                                                                      |
| 10/11 | + docstring cerca_documenti (moto, cilindrata)          | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 🟡   | ✅   | 7/8 + 1 parziale — nessun effetto                                                                     |
| 10/11 | + ISTRUZIONI: domande di consiglio su entrambe le fonti | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8                                                                                                   |
| 12/11 | dati corretti: km e giorni dalle tappe                  | ✅   | —   | ✅   | —   | —   | —   | —   | —   | solo 1 e 3 verificate                                                                                 |
| 12/11 | + docstring query_db: campi di testo con LIKE           | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8                                                                                                   |
| 12/11 | + tool cerca_testo (UNION ALL nel codice)               | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8                                                                                                   |
| 16/11 | + output_type RispostaAgente (testo + id)               | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — id corretti 8/8, domanda 8 nessuna ripetizione, nessuno scartato                                |
| 16/11 | + output_type RispostaAgente (testo + id)               | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — id corretti 8/8, nessuno scartato                                                               |
| 16/11 | + tool scheda_itinerario (da carica_itinerario)         | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — id corretti 8/8; scheda usata solo sulla 4 (2 itinerari precisi), confronti sempre con query_db |
| 19/11 | + critico dei numeri (acceso)                           | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — critico: numeri tutti nelle fonti 8/8, livello 2 mai chiamato                                   |
| 19/11 | dati coerenti (prezzo itinerari tolto, Dolomiti 8 gg)   | —   | —   | ✅   | —   | —   | —   | —   | —   | 3 rimisurata: solo Corsica (Dolomiti ora 8 giorni)                                                    |

Osservazioni:

- 12/11, griglia 1-8 con cerca_testo: la 8 rifiuta correttamente ma dichiara
  di aver cercato anche nei dati delle tappe, mentre ha chiamato solo
  cerca_documenti. Da rivedere se si ripete.

- 12/11, domanda 16: in 1 prova su 3 la Turchia viene esclusa. cerca_testo
  restituisce la nota di Istanbul, ma il modello non considera la traversata
  sul Bosforo un traghetto dell'itinerario. Il recupero è corretto, l'ambiguità
  sta nella domanda: non si corregge con le ISTRUZIONI (rischio overfitting).

- Domanda 8: 16/11 non ripetuto (dichiara correttamente dove ha cercato).

- Domanda 10a: 16/11 una volta ha definito "circolare" l'itinerario Corsica (va da Bastia a Bonifacio). Piccola invenzione, da rivedere se si ripete.
  
- Domanda 10b: risolta il 16/11 con il tool scheda_itinerario (3/3). Prima falliva 2 volte su 4: SQL su colonna inesistente, oppure tabella documenti mai letta.

- Conclusione: una frase nella docstring non bastava a ottenere SQL complesso
  corretto (JOIN cartesiano, righe tagliate a 50). La ricerca nei testi è
  stata spostata nel codice (cerca_nei_testi in strumenti.py).

### Griglia estesa 9-16

| Data  | Versione                                              | 9   | 10  | 11  | 12  | 13  | 14  | 15  | 16  | Totale                                                                                                                                                |
| ----- | ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 12/11 | baseline                                              | ✅   | ✅   | ✅   | ✅   | 🟡   | ✅   | ✅   | ✅   | 7/8 + 1 parziale (13: manca la A1 in consigli)                                                                                                        |
| 12/11 | + docstring query_db: campi di testo con LIKE         | ✅   | ✅   | ✅   | ✅   | 🟡   | ✅   | ✅   | ❌   | 6/8 + 1 parziale — JOIN cartesiano (96 righe, taglio a 50)                                                                                            |
| 12/11 | + tool cerca_testo (UNION ALL nel codice)             | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — ripetizioni: 13 → 3/3, 16 → 2/3                                                                                                                 |
| 16/11 | + output_type RispostaAgente (testo + id)             | ✅   | ❌   | ✅   | ✅   | ✅   | ✅   | ✅   | 🟡   | 6/8 + 1 parziale — 10b: query su colonna inesistente, nessun nuovo tentativo; 16: non usa cerca_testo, manca Turchia                                  |
| 16/11 | + output_type RispostaAgente (testo + id)             | ✅   | ❌   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 7/8 — ripetizioni: 10b → 2/3 (non legge la tabella documenti), 16 → 3/3 col criterio aggiornato; id validi, nessuno scartato                          |
| 16/11 | + tool scheda_itinerario (da carica_itinerario)       | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — 10b con [scheda] corsica; 16: 4 itinerari, Turchia esclusa con motivazione esplicita                                                            |
| 16/11 | + tool scheda_itinerario (da carica_itinerario)       | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — ripetizioni: 10b → 3/3 con [scheda] corsica; 16: Turchia esclusa con motivazione esplicita                                                      |
| 19/11 | + tool registra_richiesta (sotto approvazione)        | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — registra_richiesta mai chiamato; 9b Turchia 99 € (prezzo itinerario, non pacchetto); 11 senza la tappa Himarë; 16 Turchia inclusa (accettabile) |
| 19/11 | + critico dei numeri (acceso)                         | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅   | 8/8 — critico: livello 2 mai chiamato, nessun falso allarme; 11 e 12 senza la tappa (si ripete)                                                       |
| 19/11 | dati coerenti (prezzo itinerari tolto, Dolomiti 8 gg) | ✅   | ✅   | —   | —   | —   | —   | —   | —   | 9a, 9b (nuova: "più lungo") e 10a rimisurate: nessun prezzo di itinerario; 25 €249 ✅                                                                  |

### Griglia richieste 17-20

| Data  | Versione                                           | 17a | 17b | 18  | 19  | 20  | DB  | Totale                                                           |
| ----- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------------- |
| 19/11 | + registra_richiesta sotto approvazione            | ✅   | 🟡   | 🟡   | ❌   | 🟡   | ✅   | 1/5 + 3 parziali — DB: solo la richiesta approvata               |
| 19/11 | + motivo con dati verificati; conferma "approvata" | ✅   | ✅   | —   | ✅   | —   | ✅   | 17a, 17b, 19 rimisurate — 19 → 3/3 con €39 (prima €49 inventato) |

Osservazioni (19/11, prima misura):

- 17b: salva correttamente, ma dice "un operatore dovrà approvarla" quando è già
  approvata. Il testo del tool diceva solo "salvata". Corretto nel codice: il tool
  ora restituisce "approvata dall'operatore e salvata".
- 18: il modello riconosce da solo l'email incompleta e la chiede, senza chiamare
  il tool (il rifiuto nel codice resta come rete di sicurezza). Chiede anche quale
  itinerario nei Balcani, ma ce n'è uno solo: non ha consultato il DB. Da rivedere se si ripete.
- 19: dopo il rifiuto con motivo dice "Essenziale €49", il prezzo giusto è €39
  (prezzo inventato: il motivo non conteneva il prezzo). Corretto nel codice:
  al motivo dell'operatore si aggiungono itinerario e prezzo verificati.
- 20: rifiuta correttamente senza chiamare il tool, ma non propone gli itinerari
  disponibili. Accettabile, non si corregge con le ISTRUZIONI (rischio overfitting).
- 19/11, rimisura: dopo "Sì, confermo" la richiesta viene riproposta, approvata e salvata come n. 2.

### Griglia Trello 21-23

| Data  | Versione                                     | 21  | 22  | 23  | Totale                                                                     |
| ----- | -------------------------------------------- | --- | --- | --- | -------------------------------------------------------------------------- |
| 19/11 | + card su Trello via MCP (creata dal codice) | ✅   | ✅   | ✅   | 3/3 — una sola card #1 sulla board; dopo il rifiuto e il "no" nessuna card |

### Griglia trappola 24-28

| Data  | Versione       | 24  | 25  | 26  | 27  | 28  | Totale                                                                                       |
| ----- | -------------- | --- | --- | --- | --- | --- | -------------------------------------------------------------------------------------------- |
| 19/11 | critico spento | ✅   | ✅   | ✅   | ✅   | ✅   | 5/5 — 26 calcolata in SQL; 27 nessun prezzo inventato                                        |
| 19/11 | critico acceso | ✅   | ✅   | ✅   | ✅   | ✅   | 5/5 — livello 2 chiamato 1 volta su 5 (24: 128 approvato come calcolo), nessun falso allarme |

Osservazioni (19/11): la trappola non fa sbagliare l'agente, perché i numeri arrivano già dal
codice (SQL, RAG con citazioni, dati verificati nei rifiuti). Il critico non corregge nulla qui,
ma non crea falsi allarmi e costa una chiamata solo sui calcoli. Resta acceso come rete di
sicurezza; la correzione di un numero inventato è verificata dai test con modelli finti.