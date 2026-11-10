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
    testo = " | ".join(colonne) + "\n" + "\n".join(
        " | ".join("" if v is None else str(v) for v in r) for r in righe
    )
    if tagliato:
        testo += f"\n[Mostrate solo le prime {CONFIG['limite_righe']} righe: restringi la query.]"
    return testo
