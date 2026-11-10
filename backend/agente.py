"""Assistente di viaggio OnTheRoad — Agents SDK (M3·L10-L11).

Due fonti, due tool:
- query_db         → dati strutturati sugli itinerari (km, giorni, tappe, documenti…)
- cerca_documenti  → testi del sito e guide (FAQ, pacchetti, normative)

Uso:  python agente.py            (chat con sessione persistente)
"""
from agents import Agent, Runner, SQLiteSession, function_tool
from dotenv import load_dotenv

import documenti
from config import CONFIG
from strumenti import esegui_select

load_dotenv()

ISTRUZIONI = """Sei l'assistente di viaggio di OnTheRoad, piattaforma di itinerari in moto.
Rispondi in italiano, in modo pratico e conciso.

Hai due fonti:
- query_db per i dati sugli itinerari (paesi, giorni, km, difficoltà, prezzi, tappe,
  documenti, vaccinazioni, consigli);
- cerca_documenti per FAQ, pacchetti, rimborsi, contatti e guide.

Regole:
- Usa solo quello che trovi nelle fonti. Se non c'è, dillo e indica dove hai cercato.
- Quando usi un documento, cita l'[id] del passaggio.
- Per conti su km o giorni usa SQL (SUM, COUNT…), non fare i conti a mente.
"""


@function_tool
def query_db(sql: str) -> str:
    """Esegue una query SELECT in sola lettura sul database degli itinerari (SQLite).

    Tabelle:
    - itinerari(id, titolo, paese, giorni, km_totali, difficolta, stagione, prezzo_eur, riassunto)
      difficolta è uno tra 'Facile', 'Media', 'Avanzata'.
      paese può contenere più paesi separati da ' / ': usa LIKE '%Austria%'.
    - tappe(itinerario_id, ordine, nome, km, ore_guida, notti, note)
      km = distanza dalla tappa precedente; ordine 1 = partenza.
    - mezzi_tappa(itinerario_id, ordine, mezzo)
    - documenti(itinerario_id, testo)
    - vaccinazioni(itinerario_id, testo)
    - consigli(itinerario_id, testo)

    Args:
        sql: una sola query SELECT.
    """
    return esegui_select(sql)


@function_tool
def cerca_documenti(domanda: str) -> str:
    """Cerca nei testi di OnTheRoad: FAQ, pacchetti e prezzi, rimborsi, pagamenti,
    contatti, e guide su documenti e normative di viaggio.

    Args:
        domanda: la domanda riscritta in forma autonoma e completa.
    """
    try:
        return documenti.cerca(domanda)
    except NotImplementedError:
        return "Errore: la ricerca nei documenti non è ancora disponibile."


agente = Agent(
    name="Assistente OnTheRoad",
    instructions=ISTRUZIONI,
    tools=[query_db, cerca_documenti],
    model=CONFIG["modello"],
)


def main() -> None:
    sessione = SQLiteSession("chat", str(CONFIG["sessioni_db"]))
    print("Assistente OnTheRoad — scrivi 'esci' per uscire.")
    while True:
        domanda = input("\nTu: ").strip()
        if domanda.lower() in {"esci", "exit", "quit"}:
            break
        if not domanda:
            continue
        risultato = Runner.run_sync(
            agente, domanda, session=sessione, max_turns=CONFIG["max_turns"]
        )
        print(f"\nAssistente: {risultato.final_output}")


if __name__ == "__main__":
    main()
