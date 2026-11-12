"""Tool sui dati strutturati: text-to-SQL in sola lettura (pattern di M3·L8).

La sicurezza sta nel codice, non nelle istruzioni:
- connessione in sola lettura (mode=ro)
- una sola istruzione, solo SELECT
- massimo CONFIG['limite_righe'] righe
Gli errori tornano come testo, così il modello può correggersi e riprovare.
"""

import sqlite3

from config import CONFIG


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
