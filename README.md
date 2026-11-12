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
  strumenti.py     query in sola lettura sul DB
  documenti.py     ricerca nei documenti (RAG) — da collegare
  agente.py        agente con Agents SDK e sessione
  dati/            itinerari.json (fonte dei dati)
  corpus/          documenti per il RAG (FAQ, pacchetti, chi siamo)
  tests/           test senza chiave API
docs/
  domande.md       griglia di domande per misurare l'assistente
```

## Avvio

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # poi inserisci la chiave in .env

cd backend
python crea_db.py           # crea dati/itinerari.db
python -m pytest -q tests   # 8 test, non serve la chiave
python agente.py            # chat con l'assistente
```

Il frontend si apre direttamente da `frontend/index.html`.

## Tecnologie

- **Agents SDK** con due tool e sessione persistente (`SQLiteSession`)
- **Text-to-SQL** in sola lettura sugli itinerari
- **RAG** su FAQ, pacchetti e guide di viaggio *(in corso)*

## Roadmap

- [x] Repo, struttura, dati degli itinerari in SQLite, tool `query_db`
- [x] RAG sui documenti (`documenti.py`) e prima misura sulla griglia di domande
- [x] Output strutturato: un itinerario proposto dall'agente come oggetto Pydantic
- [ ] Collegamento al frontend tramite API
