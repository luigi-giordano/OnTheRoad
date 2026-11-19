# OnTheRoad AI

Assistente di viaggio con intelligenza artificiale per **OnTheRoad**, la piattaforma di itinerari in moto.

L'assistente risponde a domande come *"Ho 7 giorni a giugno, cosa mi consigli di non troppo difficile?"* o *"Quali documenti servono per l'itinerario nei Balcani?"*. Cerca nei dati degli itinerari (database SQLite) e nei testi del sito (FAQ, pacchetti, guide), e cita sempre da dove prende le informazioni.

Progetto personale del Master in AI Engineering di Boolean.

## Struttura

```
frontend/          sito OnTheRoad (HTML, CSS, JS vanilla)
backend/
  config.py        CONFIG unico del progetto
  crea_db.py       itinerari.json → itinerari.db (SQLite)
  modelli.py       modelli Pydantic: Tappa, Itinerario, Richiesta, RispostaAgente
  strumenti.py     query in sola lettura, ricerca nei testi, itinerari, richieste
  documenti.py     RAG sui documenti (chunking, embedding, Chroma)
  agente.py        agente con Agents SDK, 5 tool, sessione e approvazione
  trello_mcp.py    server MCP ufficiale di Trello: login OAuth e card delle richieste
  critico.py       generatore e critico: controllo dei numeri della risposta
  aikit/           toolkit del corso (vedi Crediti)
  dati/            itinerari.json (fonte dei dati); richieste.db si crea da solo
  corpus/          documenti per il RAG (FAQ, pacchetti, chi siamo)
  tests/           49 test, non serve la chiave API
docs/
  domande.md       griglia di 28 domande e misure dell'assistente
```

## Avvio

```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # poi inserisci la chiave in .env

cd backend
python crea_db.py           # crea dati/itinerari.db
python -m pytest -q tests   # 49 test, non serve la chiave
python trello_mcp.py        # facoltativo: login a Trello (si apre il browser, una volta sola)
python agente.py            # chat con l'assistente
```

Trello è facoltativo: senza login l'assistente funziona e salva le richieste in `richieste.db`; le card si creano dopo con `python trello_mcp.py sincronizza`. La board si chiama **Richieste OnTheRoad**, con la lista **Nuove** (nomi in `config.py`).

Il frontend si apre direttamente da `frontend/index.html`.

## Come funziona

L'agente (OpenAI Agents SDK, sessione persistente con `SQLiteSession`) sceglie tra cinque tool:

| Tool                 | Cosa fa                                                                                                   |
| -------------------- | --------------------------------------------------------------------------------------------------------- |
| `query_db`           | text-to-SQL in sola lettura per filtri e confronti (connessione `mode=ro`, solo SELECT, max 50 righe)     |
| `scheda_itinerario`  | tutti i dati di un itinerario, costruiti nel codice dal DB                                                |
| `cerca_testo`        | nomi e codici esatti (es. "SH8", "D81") su note, consigli e documenti, con termine passato come parametro |
| `cerca_documenti`    | RAG su FAQ, pacchetti e guide (22 chunk in Chroma)                                                        |
| `registra_richiesta` | richiesta di un pacchetto know-how, **sotto approvazione** di un operatore; poi card su Trello via MCP    |

Prima che l'operatore veda una richiesta, il codice la controlla: dati non validi o itinerario inesistente vengono rifiutati con un motivo che indica al modello cosa fare. Dopo il sì, la richiesta si salva in `richieste.db` (DB separato: `itinerari.db` resta in sola lettura) e il codice crea la card nella board Trello, una sola per richiesta.

La risposta è un output strutturato (`RispostaAgente`, Pydantic): testo più gli id degli itinerari citati. Gli oggetti `Itinerario` li costruisce il codice dal DB, non il modello, e gli id inesistenti vengono scartati. Così km e prezzi non possono essere inventati.

## Critico dei numeri

Km e prezzi sono quello che l'utente usa per decidere, quindi un numero inventato è l'errore peggiore. Ogni risposta passa da un controllo in due livelli (`critico.py`):

1. **codice**: estrae i numeri della risposta e controlla che compaiano nei risultati dei tool o nei messaggi dell'utente (gratis, deterministico);
2. **critico LLM**: solo se il codice trova numeri senza fonte, decide se sono calcoli corretti (es. 89 + 39 = 128) o inventati, e dice cosa cambiare.

L'agente rivede la risposta al massimo 2 volte (lo decide il codice); se non basta, la risposta mostra un avviso. Si accende e spegne con `CONFIG["critico"]`, per misurare con e senza.

## Misure

Ogni modifica viene rimisurata su tutta la griglia (`docs/domande.md`), con sessione nuova. Le domande instabili si ripetono 3 volte prima di correggere.

| Griglia | Cosa misura                                                                                         | Risultato                                 |
| ------- | --------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1-8     | dati puntuali, filtri, documenti, rifiuto fuori dominio                                             | 8/8                                       |
| 9-16    | follow-up con la sessione, codici esatti, confronti                                                 | 8/8                                       |
| 17-20   | richieste di pacchetto: dati mancanti, email non valida, rifiuto con motivo, itinerario inesistente | rifiuto con motivo 3/3 dopo la correzione |
| 21-23   | card su Trello: creazione, idempotenza, nessuna card se rifiutata                                   | 3/3                                       |
| 24-28   | trappola sui numeri, con e senza critico                                                            | 5/5 in entrambi i casi                    |

## Scelte di progetto

Le decisioni principali, ognuna presa dopo una misura:

1. **Quello che deve essere affidabile va nel codice, non nel prompt.** Una frase nella docstring non bastava per ottenere SQL corretto: un JOIN su cinque tabelle generava 96 righe, tagliate a 50, e la risposta giusta spariva. Per questo la ricerca nei testi (`cerca_testo`), la scheda di un itinerario (`scheda_itinerario`), i prezzi dei pacchetti e la creazione delle card sono scritti nel codice.
2. **Il modello restituisce id, non dati.** `RispostaAgente` contiene solo gli id degli itinerari; gli oggetti `Itinerario` li carica il codice dal DB e gli id inesistenti vengono scartati. Così km e prezzi non possono essere riscritti male.
3. **Le tappe sono la fonte di verità, e i dati non si contraddicono.** `distance` è la somma dei km delle tappe e `days` sono le notti + 1 (validator Pydantic e due test). Le incoerenze trovate misurando sono state corrette: km dichiarati diversi dalla somma delle tappe, un paese senza tappe, una tappa troppo lunga per una giornata (divisa in due), un prezzo per itinerario che contraddiceva i pacchetti a prezzo fisso (tolto). Il frontend usa gli stessi dati del backend.
4. **Il codice controlla prima dell'operatore.** Nell'approvazione, dati non validi e itinerari inesistenti vengono rifiutati dal codice. Quando l'operatore rifiuta con un motivo, il codice aggiunge i dati verificati: senza, il modello aveva inventato un prezzo (€49 invece di €39).
5. **MCP per l'app di altri, chiamato dal codice.** Trello è un servizio esterno, quindi si usa il suo server MCP ufficiale. La card però non la crea il modello: è una conseguenza garantita dell'approvazione, con un controllo di idempotenza (`#N` già presente → nessuna nuova card).
6. **Il critico è stato misurato prima di tenerlo.** Sulla griglia trappola l'agente non sbaglia neanche senza critico, perché i numeri arrivano già dal codice. Il critico resta acceso perché il primo livello è gratis e il secondo scatta solo sui calcoli (1 volta su 5), senza falsi allarmi.
7. **Niente skill, per ora.** L'agente chiede già da solo i dati mancanti di una richiesta con quattro righe di istruzioni (domanda 17a). Una skill serve per procedure lunghe e usate di rado: qui non c'era un problema da risolvere.
8. **Nessuna correzione per far tornare la griglia.** Quando una risposta è ambigua (domanda 16, il Bosforo è un traghetto?) si corregge la risposta attesa, non le istruzioni, per non adattare l'agente alle domande di prova.

## Roadmap

- [x] Repo, struttura, dati degli itinerari in SQLite, tool `query_db`
- [x] RAG sui documenti e prima misura sulla griglia di domande
- [x] Tool dedicati `cerca_testo` e `scheda_itinerario`, griglia estesa a 16 domande
- [x] Output strutturato con Pydantic, id verificati nel codice
- [x] Richiesta di pacchetto sotto approvazione (M4)
- [x] MCP con Trello: card per ogni richiesta approvata, con idempotenza (M4)
- [x] Generatore e critico sui numeri, misurato su una griglia trappola (M4)
- [ ] API FastAPI collegata al frontend, deploy (M5)

## Crediti

- **aikit** (`backend/aikit/`): toolkit didattico del Master AI Engineering di Boolean, copiato dalla lezione M3·L12. Lo uso per il caricamento e la pulizia dei documenti, il chunking, gli embedding e il vector store. Le parti scritte per questo progetto sono `config.py`, `crea_db.py`, `modelli.py`, `strumenti.py`, `documenti.py`, `agente.py` e i test.
- **Frontend** (`frontend/`): sito OnTheRoad originale, copiato invariato dalla sua repo pubblica.