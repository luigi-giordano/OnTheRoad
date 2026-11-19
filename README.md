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
  modelli.py       modelli Pydantic: Tappa, Itinerario, RispostaAgente
  strumenti.py     query in sola lettura, ricerca nei testi, caricamento itinerari
  documenti.py     RAG sui documenti (chunking, embedding, Chroma)
  agente.py        agente con Agents SDK, 5 tool, sessione e approvazione
  aikit/           toolkit del corso (vedi Crediti)
  dati/            itinerari.json (fonte dei dati)
  corpus/          documenti per il RAG (FAQ, pacchetti, chi siamo)
  tests/           37 test, non serve la chiave API
docs/
  domande.md       griglia di 16 domande e misure dell'assistente
```

## Avvio

```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # poi inserisci la chiave in .env

cd backend
python crea_db.py           # crea dati/itinerari.db
python -m pytest -q tests   # 37 test, non serve la chiave
python agente.py            # chat con l'assistente
```

Il frontend si apre direttamente da `frontend/index.html`.

## Come funziona

L'agente (OpenAI Agents SDK, sessione persistente con `SQLiteSession`) sceglie tra cinque tool:

| Tool                | Cosa fa                                                                                                   |
| ------------------- | --------------------------------------------------------------------------------------------------------- |
| `query_db`          | text-to-SQL in sola lettura per filtri e confronti (connessione `mode=ro`, solo SELECT, max 50 righe)     |
| `scheda_itinerario` | tutti i dati di un itinerario, costruiti nel codice dal DB                                                |
| `cerca_testo`       | nomi e codici esatti (es. "SH8", "D81") su note, consigli e documenti, con termine passato come parametro |
| `cerca_documenti`   | RAG su FAQ, pacchetti e guide (22 chunk in Chroma)                                                        |

La risposta è un output strutturato (`RispostaAgente`, Pydantic): testo più gli id degli itinerari citati. Gli oggetti `Itinerario` li costruisce il codice dal DB, non il modello, e gli id inesistenti vengono scartati. Così km e prezzi non possono essere inventati.

## Misure

Ogni modifica viene rimisurata su una griglia di 16 domande (`docs/domande.md`), con sessione nuova: dati puntuali, filtri, follow-up con la sessione, codici esatti, confronti e una domanda fuori dominio che deve essere rifiutata.

Risultato attuale: **8/8** sulla griglia 1-8 e **8/8** sulla griglia 9-16.

## Roadmap

- [x] Repo, struttura, dati degli itinerari in SQLite, tool `query_db`
- [x] RAG sui documenti e prima misura sulla griglia di domande
- [x] Tool dedicati `cerca_testo` e `scheda_itinerario`, griglia estesa a 16 domande
- [x] Output strutturato con Pydantic, id verificati nel codice
- [x] Richiesta di pacchetto sotto approvazione (M4)
- [ ] Skill, MCP con Trello, generatore e critico (M4)
- [ ] API FastAPI collegata al frontend, deploy (M5)

## Crediti

- **aikit** (`backend/aikit/`): toolkit didattico del Master AI Engineering di Boolean, copiato dalla lezione M3·L12. Lo uso per il caricamento e la pulizia dei documenti, il chunking, gli embedding e il vector store. Le parti scritte per questo progetto sono `config.py`, `crea_db.py`, `modelli.py`, `strumenti.py`, `documenti.py`, `agente.py` e i test.
- **Frontend** (`frontend/`): sito OnTheRoad originale, copiato invariato dalla sua repo pubblica.