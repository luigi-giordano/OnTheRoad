"""Assistente di viaggio OnTheRoad — Agents SDK (M3·L10-L11).

Tre tool su due fonti:
- query_db         → dati strutturati sugli itinerari (km, giorni, tappe, documenti…)
- cerca_testo      → nomi e codici in tutti i testi degli itinerari (UNION ALL nel codice)
- cerca_documenti  → testi del sito e guide (FAQ, pacchetti, normative)

Output strutturato: RispostaAgente (testo + id degli itinerari citati).

Uso:  python agente.py            (chat con sessione persistente)
"""

from agents import Agent, Runner, SQLiteSession, function_tool
from dotenv import load_dotenv

import documenti
from config import CONFIG
from modelli import RispostaAgente
from strumenti import carica_itinerario, cerca_nei_testi, esegui_select

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
- Per domande di consiglio (se un viaggio è adatto a una moto, a una cilindrata,
  a un livello di esperienza, a una stagione) consulta sempre entrambe le fonti:
  query_db per i dati dell'itinerario e cerca_documenti per i consigli.
- Non dire che le fonti non specificano qualcosa se non le hai consultate tutte.

Formato della risposta:
- testo: la risposta per l'utente.
- itinerari: gli id (colonna id della tabella itinerari, es. 'albania-loop') degli
  itinerari di cui parli. Prendili dai risultati di query_db, non inventarli.
  Lista vuota se la risposta non riguarda itinerari specifici.
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
    - per cercare un nome o un codice nei testi (strade, luoghi, mezzi come
      traghetti) non usare LIKE qui: usa cerca_testo.

    Args:
        sql: una sola query SELECT.
    """
    print(f"  [sql] {sql}")
    return esegui_select(sql)


@function_tool
def cerca_testo(termine: str) -> str:
    """Cerca un nome o un codice in tutti i testi degli itinerari: riassunti,
    note delle tappe, mezzi, consigli, documenti, vaccinazioni.
    Da usare per strade (SH8, D81, A1), luoghi e mezzi (traghetto, barca).
    Restituisce itinerario, campo e testo di ogni occorrenza.

    Args:
        termine: solo la parola o il codice da cercare, es. "A1" o "traghett".
    """
    print(f"  [testo] {termine}")
    return cerca_nei_testi(termine)


@function_tool
def cerca_documenti(domanda: str) -> str:
    """Cerca nei testi di OnTheRoad: FAQ, pacchetti e prezzi, rimborsi, pagamenti,
    contatti, guide su documenti e normative di viaggio, e consigli pratici
    di chi ha fatto i viaggi (moto adatte e cilindrata, strade, difficoltà).

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
    model=CONFIG["modello"],
    tools=[query_db, cerca_testo, cerca_documenti],
    output_type=RispostaAgente,
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
        risposta: RispostaAgente = risultato.final_output
        print(f"\nAssistente: {risposta.testo}")

        # Controllo nel codice: un id inventato dal modello non arriva al frontend.
        validi = [i for i in risposta.itinerari if carica_itinerario(i) is not None]
        scartati = [i for i in risposta.itinerari if i not in validi]
        print(f"  [itinerari] {validi}")
        if scartati:
            print(f"  [scartati] {scartati}")


if __name__ == "__main__":
    main()
