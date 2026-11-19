"""Assistente di viaggio OnTheRoad — Agents SDK (M3·L10-L11, M4·L5).

Quattro tool in lettura su due fonti:
- query_db           → dati strutturati sugli itinerari (km, giorni, tappe, documenti…)
- scheda_itinerario  → tutti i dati di UN itinerario, senza SQL (costruita nel codice)
- cerca_testo        → nomi e codici in tutti i testi degli itinerari (UNION ALL nel codice)
- cerca_documenti    → testi del sito e guide (FAQ, pacchetti, normative)

Un tool che scrive, sotto approvazione:
- registra_richiesta → richiesta di un pacchetto know-how, salvata in richieste.db
                       solo dopo il sì dell'operatore (gestisci_approvazioni),
                       poi card nella board Trello via MCP (trello_mcp.py)

Output strutturato: RispostaAgente (testo + id degli itinerari citati).

Uso:  python agente.py            (chat con sessione persistente)
"""

import asyncio
import json
from contextlib import AsyncExitStack

from agents import Agent, Runner, SQLiteSession, function_tool
from dotenv import load_dotenv
from pydantic import ValidationError

import documenti
from config import CONFIG
from modelli import Richiesta, RispostaAgente
from strumenti import (
    PREZZI_PACCHETTI,
    carica_itinerario,
    cerca_nei_testi,
    esegui_select,
    riepilogo_richiesta,
    salva_richiesta,
    scheda_come_testo,
)
from trello_mcp import crea_card_richiesta, server_trello

load_dotenv()

ISTRUZIONI = """Sei l'assistente di viaggio di OnTheRoad, piattaforma di itinerari in moto.
Rispondi in italiano, in modo pratico e conciso.

Hai due fonti:
- i dati sugli itinerari (paesi, giorni, km, difficoltà, prezzi, tappe, documenti,
  vaccinazioni, consigli): query_db per confronti e filtri tra itinerari,
  scheda_itinerario per tutti i dati di un itinerario preciso;
- cerca_documenti per FAQ, pacchetti, rimborsi, contatti e guide.

Regole:
- Usa solo quello che trovi nelle fonti. Se non c'è, dillo e indica dove hai cercato.
- Quando usi un documento, cita l'[id] del passaggio.
- Per conti su km o giorni usa SQL (SUM, COUNT…), non fare i conti a mente.
- Per domande di consiglio (se un viaggio è adatto a una moto, a una cilindrata,
  a un livello di esperienza, a una stagione) consulta sempre entrambe le fonti:
  query_db per i dati dell'itinerario e cerca_documenti per i consigli.
- Non dire che le fonti non specificano qualcosa se non le hai consultate tutte.
- Quando la domanda riguarda un itinerario preciso (descrizione, tappe, documenti,
  vaccinazioni, consigli), anche se è stato nominato in un messaggio precedente,
  usa scheda_itinerario con il suo id.

Richieste di pacchetti:
- Se l'utente vuole acquistare un pacchetto (Essenziale, Completo, Su misura) per un
  itinerario, servono nome, email, itinerario e pacchetto. Chiedi quelli che mancano,
  senza inventarli. Le date o le esigenze vanno nel messaggio (vuoto se non le dice).
- Quando hai tutti i dati, usa registra_richiesta. Un operatore deve approvarla:
  se la rifiuta, segui il motivo che ti dà e non riprovare uguale.
- Dopo il salvataggio conferma numero e prezzo restituiti dal tool, e che arriverà
  un'email con il link di pagamento.

Formato della risposta:
- testo: la risposta per l'utente.
- itinerari: gli id (colonna id della tabella itinerari, es. 'albania-loop') degli
  itinerari di cui parli. Prendili dai risultati dei tool, non inventarli.
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
def scheda_itinerario(id_itinerario: str) -> str:
    """Restituisce tutti i dati di UN itinerario: dati generali, tappe con km,
    ore, notti, mezzi e note, documenti, vaccinazioni e consigli.
    Da usare per descrivere un itinerario o rispondere su documenti, tappe e
    consigli di un itinerario preciso. Per confronti tra itinerari usa query_db.

    Args:
        id_itinerario: l'id dell'itinerario, es. "corsica" o "albania-loop".
    """
    print(f"  [scheda] {id_itinerario}")
    return scheda_come_testo(id_itinerario)


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


# Connessione a Trello, aperta in main(). None se Trello non è raggiungibile:
# la richiesta si salva comunque, senza card.
TRELLO = None


@function_tool(needs_approval=True)
async def registra_richiesta(richiesta: Richiesta) -> str:
    """Registra la richiesta di un pacchetto know-how per un itinerario.
    Va usata solo quando l'utente ha dato nome, email, itinerario e pacchetto.
    Un operatore deve approvarla prima del salvataggio.

    Args:
        richiesta: i dati della richiesta, come nel modulo della pagina Offerte.
    """
    if carica_itinerario(richiesta.itinerary_id) is None:
        return (
            f"Errore: l'itinerario '{richiesta.itinerary_id}' non esiste. "
            "Usa query_db per vedere gli id disponibili."
        )
    numero = salva_richiesta(richiesta)
    prezzo = PREZZI_PACCHETTI[richiesta.package]
    print(f"  [richiesta] n. {numero} salvata")

    # Card su Trello: la crea il codice (M4·L8-L9), una volta sola per numero.
    # Un errore di Trello non annulla la richiesta: è già salvata in richieste.db.
    if TRELLO is None:
        esito_card = "card non creata: Trello non collegato"
    else:
        try:
            esito_card = await crea_card_richiesta(
                TRELLO, numero, carica_itinerario(richiesta.itinerary_id).title,
                richiesta.package, prezzo, richiesta.name, richiesta.email,
                richiesta.message,
            )
        except Exception as e:
            esito_card = f"card non creata: {e}"
    print(f"  [trello] {esito_card}")

    return (
        f"Richiesta n. {numero} approvata dall'operatore e salvata: "
        f"pacchetto {richiesta.package}, €{prezzo}. "
        "Arriverà un'email con il link di pagamento."
    )


agente = Agent(
    name="Assistente OnTheRoad",
    instructions=ISTRUZIONI,
    model=CONFIG["modello"],
    tools=[query_db, scheda_itinerario, cerca_testo, cerca_documenti, registra_richiesta],
    output_type=RispostaAgente,
)


async def gestisci_approvazioni(risultato, sessione):
    """Ciclo di approvazione (M4·L5): finché l'agente si ferma su un tool
    da approvare, mostra il riepilogo costruito dal codice e chiede sì o no.

    Prima dell'operatore controlla il codice: dati non validi o itinerario
    inesistente vengono rifiutati con un motivo che indica al modello la strada.
    Un no dell'operatore senza motivo ferma il modello; con un motivo lo guida.
    """
    while risultato.interruptions:
        stato = risultato.to_state()
        for item in risultato.interruptions:
            try:
                richiesta = Richiesta.model_validate(json.loads(item.arguments)["richiesta"])
            except ValidationError as e:
                # Dati non validi: li rifiuta il codice, senza disturbare l'operatore.
                errori = "; ".join(err["msg"] for err in e.errors())
                print(f"  [rifiutata dal codice] {errori}")
                stato.reject(
                    item,
                    rejection_message=f"Dati non validi ({errori}). "
                    "Chiedi all'utente di correggerli, poi riprova.",
                )
                continue
            if carica_itinerario(richiesta.itinerary_id) is None:
                print(f"  [rifiutata dal codice] itinerario '{richiesta.itinerary_id}' inesistente")
                stato.reject(
                    item,
                    rejection_message=f"L'itinerario '{richiesta.itinerary_id}' non esiste. "
                    "Dillo all'utente e proponi quelli disponibili (query_db).",
                )
                continue
            print("\n  [approvazione] nuova richiesta di pacchetto")
            print(riepilogo_richiesta(richiesta))
            if input("  Approvi? (s/n): ").strip().lower() == "s":
                stato.approve(item)
            else:
                motivo = input("  Motivo (invio per nessuno): ").strip()
                if motivo:
                    # Al motivo il codice aggiunge i dati verificati: il modello
                    # non deve ricordare o inventare il prezzo (misura del 19/11, domanda 19).
                    it = carica_itinerario(richiesta.itinerary_id)
                    motivo += (
                        f". Dati verificati della richiesta: itinerario {it.title}, "
                        f"pacchetto {richiesta.package} a €{PREZZI_PACCHETTI[richiesta.package]}."
                    )
                stato.reject(item, rejection_message=motivo or None)
                print("  [rifiutata]")
        risultato = await Runner.run(
            agente, stato, session=sessione, max_turns=CONFIG["max_turns"]
        )
    return risultato


async def main() -> None:
    """Chat async (come l'assistente di M4·L4): la connessione MCP a Trello vive
    nello stesso event loop per tutta la chat, invece di riaprirsi a ogni domanda."""
    global TRELLO
    sessione = SQLiteSession("chat", str(CONFIG["sessioni_db"]))
    async with AsyncExitStack() as pila:
        try:
            TRELLO = await pila.enter_async_context(server_trello())
            print("  [trello] collegato")
        except Exception as e:
            print(f"  [trello] non collegato ({e}): le richieste si salvano senza card")

        print("Assistente OnTheRoad — scrivi 'esci' per uscire.")
        while True:
            domanda = input("\nTu: ").strip()
            if domanda.lower() in {"esci", "exit", "quit"}:
                break
            if not domanda:
                continue
            risultato = await Runner.run(
                agente, domanda, session=sessione, max_turns=CONFIG["max_turns"]
            )
            risultato = await gestisci_approvazioni(risultato, sessione)
            risposta: RispostaAgente = risultato.final_output
            print(f"\nAssistente: {risposta.testo}")

            # Controllo nel codice: un id inventato dal modello non arriva al frontend.
            validi = [i for i in risposta.itinerari if carica_itinerario(i) is not None]
            scartati = [i for i in risposta.itinerari if i not in validi]
            print(f"  [itinerari] {validi}")
            if scartati:
                print(f"  [scartati] {scartati}")


if __name__ == "__main__":
    asyncio.run(main())
