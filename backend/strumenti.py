"""Tool sui dati strutturati: text-to-SQL in sola lettura (pattern di M3·L8).

La sicurezza sta nel codice, non nelle istruzioni:
- connessione in sola lettura (mode=ro)
- una sola istruzione, solo SELECT
- massimo CONFIG['limite_righe'] righe
Gli errori tornano come testo, così il modello può correggersi e riprovare.
"""

import sqlite3

from config import CONFIG
from modelli import Itinerario, Richiesta


def esegui_select(sql: str) -> str:
    sql = sql.strip().rstrip(";").strip()
    if ";" in sql:
        return "Errore: una sola istruzione SQL per volta."
    if not sql.lower().startswith(("select", "with")):
        return "Errore: sono permesse solo query SELECT."
    uri = f"file:{CONFIG['db_path'].as_posix()}?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True)
        try:
            cur = con.execute(sql)
            colonne = [c[0] for c in cur.description]
            righe = cur.fetchmany(CONFIG["limite_righe"] + 1)
        finally:
            con.close()
    except sqlite3.Error as e:
        return f"Errore: {e}"

    if not righe:
        return "Nessun risultato."
    tagliato = len(righe) > CONFIG["limite_righe"]
    righe = righe[: CONFIG["limite_righe"]]
    testo = (
        " | ".join(colonne)
        + "\n"
        + "\n".join(" | ".join("" if v is None else str(v) for v in r) for r in righe)
    )
    if tagliato:
        testo += f"\n[Mostrate solo le prime {CONFIG['limite_righe']} righe: restringi la query.]"
    return testo


SQL_TESTI = """
SELECT i.titolo, 'riassunto', i.riassunto
  FROM itinerari i WHERE i.riassunto LIKE :p
UNION ALL
SELECT i.titolo, 'tappa: ' || t.nome, t.note
  FROM tappe t JOIN itinerari i ON i.id = t.itinerario_id
 WHERE t.note LIKE :p
UNION ALL
SELECT i.titolo, 'mezzo, tappa: ' || t.nome, m.mezzo
  FROM mezzi_tappa m
  JOIN tappe t ON t.itinerario_id = m.itinerario_id AND t.ordine = m.ordine
  JOIN itinerari i ON i.id = m.itinerario_id
 WHERE m.mezzo LIKE :p
UNION ALL
SELECT i.titolo, 'consiglio', c.testo
  FROM consigli c JOIN itinerari i ON i.id = c.itinerario_id
 WHERE c.testo LIKE :p
UNION ALL
SELECT i.titolo, 'documento', d.testo
  FROM documenti d JOIN itinerari i ON i.id = d.itinerario_id
 WHERE d.testo LIKE :p
UNION ALL
SELECT i.titolo, 'vaccinazione', v.testo
  FROM vaccinazioni v JOIN itinerari i ON i.id = v.itinerario_id
 WHERE v.testo LIKE :p
"""


def cerca_nei_testi(termine: str) -> str:
    """Cerca un termine in tutti i campi di testo, con una UNION ALL già scritta.

    Il termine passa come parametro (:p), mai dentro la stringa SQL:
    niente injection, e gli apostrofi non rompono la query.
    """
    termine = termine.strip()
    if not termine:
        return "Errore: termine vuoto."
    uri = f"file:{CONFIG['db_path'].as_posix()}?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True)
        try:
            righe = con.execute(SQL_TESTI, {"p": f"%{termine}%"}).fetchmany(
                CONFIG["limite_righe"] + 1
            )
        finally:
            con.close()
    except sqlite3.Error as e:
        return f"Errore: {e}"

    if not righe:
        return f"Nessun testo contiene '{termine}'."
    tagliato = len(righe) > CONFIG["limite_righe"]
    righe = righe[: CONFIG["limite_righe"]]
    testo = "itinerario | campo | testo\n" + "\n".join(" | ".join(r) for r in righe)
    if tagliato:
        testo += f"\n[Mostrate solo le prime {CONFIG['limite_righe']} righe: usa un termine più specifico.]"
    return testo


def carica_itinerario(id_: str) -> Itinerario | None:
    """Costruisce un Itinerario dal DB, senza LLM: dati esatti per il frontend.

    Restituisce None se l'id non esiste. Se i dati nel DB sono incoerenti,
    Pydantic solleva ValidationError (meglio un errore che un dato sbagliato).
    """
    uri = f"file:{CONFIG['db_path'].as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    try:
        it = con.execute("SELECT * FROM itinerari WHERE id = ?", (id_,)).fetchone()
        if it is None:
            return None

        def lista(sql: str, *param) -> list[str]:
            return [r[0] for r in con.execute(sql, (id_, *param))]

        tappe = con.execute(
            "SELECT * FROM tappe WHERE itinerario_id = ? ORDER BY ordine", (id_,)
        ).fetchall()
        stops = [
            {
                "name": t["nome"],
                "km": t["km"],
                "hours": t["ore_guida"] or "",
                "nights": t["notti"],
                "notes": t["note"] or "",
                "transport": lista(
                    "SELECT mezzo FROM mezzi_tappa WHERE itinerario_id = ? AND ordine = ?"
                    " ORDER BY rowid",
                    t["ordine"],
                ),
                "photos": lista(
                    "SELECT url FROM foto_tappa WHERE itinerario_id = ? AND ordine = ?"
                    " ORDER BY posizione",
                    t["ordine"],
                ),
            }
            for t in tappe
        ]
        return Itinerario(
            id=it["id"],
            title=it["titolo"],
            country=it["paese"],
            duration=f"{it['giorni']} giorni",
            days=it["giorni"],
            distance=it["km_totali"],
            difficulty=it["difficolta"],
            season=it["stagione"] or "",
            price=it["prezzo_eur"],
            cover=it["cover"] or "",
            summary=it["riassunto"] or "",
            stops=stops,
            documents=lista(
                "SELECT testo FROM documenti WHERE itinerario_id = ? ORDER BY rowid"
            ),
            vaccinations=lista(
                "SELECT testo FROM vaccinazioni WHERE itinerario_id = ? ORDER BY rowid"
            ),
            tips=lista(
                "SELECT testo FROM consigli WHERE itinerario_id = ? ORDER BY rowid"
            ),
        )
    finally:
        con.close()


def scheda_come_testo(id_: str) -> str:
    """Tutti i dati di un itinerario come testo, costruiti da carica_itinerario.

    Nessun SQL scritto dal modello: i dati arrivano sempre completi
    (tappe, mezzi, documenti, vaccinazioni, consigli).
    """
    it = carica_itinerario(id_.strip())
    if it is None:
        return (
            f"Errore: nessun itinerario con id '{id_}'. Usa query_db per trovare l'id."
        )
    righe = [
        f"{it.title} (id: {it.id})",
        f"Paese: {it.country} | {it.days} giorni | {it.distance} km | "
        f"difficoltà {it.difficulty} | stagione {it.season} | {it.price} €",
        f"Riassunto: {it.summary}",
        "Tappe:",
    ]
    for n, t in enumerate(it.stops, start=1):
        mezzi = ", ".join(t.transport) or "—"
        ore = t.hours or "—"
        righe.append(
            f"  {n}. {t.name} — {t.km} km, {ore}, {t.nights} notti, mezzi: {mezzi}"
        )
        if t.notes:
            righe.append(f"     note: {t.notes}")
    for titolo, voci in (
        ("Documenti", it.documents),
        ("Vaccinazioni", it.vaccinations),
        ("Consigli", it.tips),
    ):
        righe.append(f"{titolo}:")
        righe.extend(f"  - {v}" for v in voci)
    return "\n".join(righe)


# --- Richieste di pacchetti (M4) ---------------------------------------------
# Prezzi dei pacchetti know-how, come nel modulo della pagina Offerte.
# Decisione del 19/11: la richiesta costa il prezzo del pacchetto;
# il price dell'itinerario è un valore da chiarire (Problemi noti).
PREZZI_PACCHETTI = {"Essenziale": 39, "Completo": 89, "Su misura": 249}

SQL_CREA_RICHIESTE = """
CREATE TABLE IF NOT EXISTS richieste (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    creata       TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    name         TEXT NOT NULL,
    email        TEXT NOT NULL,
    itinerary_id TEXT NOT NULL,
    package      TEXT NOT NULL,
    prezzo_eur   INTEGER NOT NULL,
    message      TEXT NOT NULL
)
"""


def salva_richiesta(r: Richiesta) -> int:
    """Salva una richiesta in richieste.db e restituisce il suo numero.

    Unica funzione del progetto che scrive: DB separato da itinerari.db,
    che resta in sola lettura. Il prezzo lo decide il codice, non il modello.
    """
    con = sqlite3.connect(CONFIG["richieste_db"])
    try:
        con.execute(SQL_CREA_RICHIESTE)
        cur = con.execute(
            "INSERT INTO richieste (name, email, itinerary_id, package, prezzo_eur, message)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (r.name, r.email, r.itinerary_id, r.package,
             PREZZI_PACCHETTI[r.package], r.message),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def riepilogo_richiesta(r: Richiesta) -> str:
    """Il testo che vede chi approva: costruito dal codice e dal DB, non dal modello."""
    it = carica_itinerario(r.itinerary_id)
    titolo = it.title if it else f"⚠ itinerario inesistente: '{r.itinerary_id}'"
    return (
        f"  Itinerario: {titolo}\n"
        f"  Pacchetto:  {r.package} — €{PREZZI_PACCHETTI[r.package]}\n"
        f"  Cliente:    {r.name} <{r.email}>\n"
        f"  Messaggio:  {r.message or '—'}"
    )
