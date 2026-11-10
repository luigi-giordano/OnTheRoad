"""Converte dati/itinerari.json (esportato da SAMPLE_ITINERARIES di frontend/app.js)
in un database SQLite interrogabile dall'agente con query_db.

Uso:  python crea_db.py
Il DB si rigenera da zero ogni volta: la fonte di verità è il JSON.
"""
import json
import sqlite3

from config import CONFIG

SCHEMA = """
CREATE TABLE itinerari (
    id          TEXT PRIMARY KEY,
    titolo      TEXT NOT NULL,
    paese       TEXT NOT NULL,   -- può contenere più paesi separati da ' / '
    giorni      INTEGER NOT NULL,
    km_totali   INTEGER NOT NULL,
    difficolta  TEXT NOT NULL CHECK (difficolta IN ('Facile','Media','Avanzata')),
    stagione    TEXT,            -- testo libero, es. 'Giugno – Agosto'
    prezzo_eur  INTEGER NOT NULL,
    riassunto   TEXT
);
CREATE TABLE tappe (
    itinerario_id TEXT NOT NULL REFERENCES itinerari(id),
    ordine        INTEGER NOT NULL,   -- 1 = prima tappa
    nome          TEXT NOT NULL,
    km            INTEGER NOT NULL,   -- km dalla tappa precedente (0 = partenza)
    ore_guida     TEXT,               -- testo, es. '3h 30m'
    notti         INTEGER NOT NULL,
    note          TEXT,
    PRIMARY KEY (itinerario_id, ordine)
);
CREATE TABLE mezzi_tappa (
    itinerario_id TEXT NOT NULL,
    ordine        INTEGER NOT NULL,
    mezzo         TEXT NOT NULL       -- es. 'Moto', 'Traghetto Flåm–Gudvangen'
);
CREATE TABLE documenti   (itinerario_id TEXT NOT NULL, testo TEXT NOT NULL);
CREATE TABLE vaccinazioni(itinerario_id TEXT NOT NULL, testo TEXT NOT NULL);
CREATE TABLE consigli    (itinerario_id TEXT NOT NULL, testo TEXT NOT NULL);
"""


def crea_db() -> None:
    itinerari = json.loads(CONFIG["itinerari_json"].read_text(encoding="utf-8"))
    db = CONFIG["db_path"]
    db.unlink(missing_ok=True)

    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    for it in itinerari:
        con.execute(
            "INSERT INTO itinerari VALUES (?,?,?,?,?,?,?,?,?)",
            (it["id"], it["title"], it["country"], it["days"], it["distance"],
             it["difficulty"], it.get("season"), it.get("price", 0), it.get("summary")),
        )
        for n, s in enumerate(it["stops"], start=1):
            con.execute(
                "INSERT INTO tappe VALUES (?,?,?,?,?,?,?)",
                (it["id"], n, s["name"], s.get("km", 0), s.get("hours") or None,
                 s.get("nights", 0), s.get("notes")),
            )
            con.executemany(
                "INSERT INTO mezzi_tappa VALUES (?,?,?)",
                [(it["id"], n, m) for m in s.get("transport", [])],
            )
        for tabella, chiave in (("documenti", "documents"),
                                ("vaccinazioni", "vaccinations"),
                                ("consigli", "tips")):
            con.executemany(
                f"INSERT INTO {tabella} VALUES (?,?)",
                [(it["id"], t) for t in it.get(chiave, [])],
            )
    con.commit()
    n_it = con.execute("SELECT COUNT(*) FROM itinerari").fetchone()[0]
    n_tp = con.execute("SELECT COUNT(*) FROM tappe").fetchone()[0]
    con.close()
    print(f"Creato {db.name}: {n_it} itinerari, {n_tp} tappe")


if __name__ == "__main__":
    crea_db()
