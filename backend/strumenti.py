"""Tool sui dati strutturati: text-to-SQL in sola lettura (pattern di M3·L8).

La sicurezza sta nel codice, non nelle istruzioni:
- connessione in sola lettura (mode=ro)
- una sola istruzione, solo SELECT
- massimo CONFIG['limite_righe'] righe
Gli errori tornano come testo, così il modello può correggersi e riprovare.
"""

import sqlite3

from config import CONFIG
from modelli import Itinerario


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
