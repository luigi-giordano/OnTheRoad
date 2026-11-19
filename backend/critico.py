"""Generatore e critico (M4·L12) per i numeri delle risposte.

Il problema misurato (domanda 19 del 19/11): l'agente ha scritto "€49"
per un pacchetto che costa €39. Un numero inventato è l'errore peggiore
per OnTheRoad, perché km e prezzi sono quello che l'utente usa per decidere.

Due livelli, dal più economico:
1. codice (gratis, deterministico): estrae i numeri dalla risposta e controlla
   che compaiano nelle fonti del giro (risultati dei tool e messaggi dell'utente);
2. critico LLM (una chiamata, solo se il livello 1 trova numeri senza fonte):
   decide se sono calcoli corretti fatti con i numeri delle fonti (es. 89 + 39 = 128)
   o numeri inventati, e in quel caso dice cosa cambiare.

Quanti giri di revisione fare lo decide il codice (agente.py), non il modello.
"""

import json
import re

from agents import Agent, Runner
from pydantic import BaseModel, Field

from config import CONFIG

# I messaggi di revisione che il codice manda all'agente: non sono fonti,
# altrimenti un numero sbagliato citato nella revisione diventerebbe "trovato".
MARCATORE = "[Revisione interna]"

# Numeri troppo comuni per dire qualcosa ("1 pacchetto", "2 itinerari").
IGNORATI = {"0", "1", "2"}


def numeri_nel_testo(testo: str) -> set[str]:
    """I numeri di un testo, in forma canonica: '1.140' → '1140', '5,5' → '5.5'.

    Le citazioni tra parentesi quadre ([faq-007], [albania-loop]) non contano.
    """
    testo = re.sub(r"\[[^\]]*\]", " ", testo)
    trovati = set()
    for grezzo in re.findall(r"\d+(?:[.,]\d+)*", testo):
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", grezzo):  # migliaia all'italiana
            grezzo = grezzo.replace(".", "")
        grezzo = grezzo.replace(",", ".")
        try:
            valore = float(grezzo)
        except ValueError:  # es. "1.2.3"
            continue
        canonico = f"{valore:g}" if valore != int(valore) else str(int(valore))
        if canonico not in IGNORATI:
            trovati.add(canonico)
    return trovati


def _come_testo(contenuto) -> str:
    if isinstance(contenuto, str):
        return contenuto
    if isinstance(contenuto, list):  # parti di un messaggio: [{"type": ..., "text": ...}]
        return " ".join(p.get("text", "") for p in contenuto if isinstance(p, dict))
    return json.dumps(contenuto, ensure_ascii=False)


def fonti_dalla_sessione(items: list) -> str:
    """Le fonti ammesse: risultati dei tool e messaggi dell'utente della sessione.

    Non contano le risposte dell'assistente (un numero inventato ripetuto
    non diventa vero) né i messaggi di revisione del codice.
    """
    parti = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "function_call_output":
            parti.append(_come_testo(item.get("output", "")))
        elif item.get("role") == "user":
            testo = _come_testo(item.get("content", ""))
            if not testo.startswith(MARCATORE):
                parti.append(testo)
    return "\n".join(parti)


def numeri_senza_fonte(risposta: str, fonti: str) -> set[str]:
    """Livello 1 del critico: i numeri della risposta che non compaiono nelle fonti."""
    return numeri_nel_testo(risposta) - numeri_nel_testo(fonti)


class Critica(BaseModel):
    approvata: bool = Field(
        description="true se ogni numero segnalato è un calcolo corretto fatto con "
        "i numeri delle fonti; false se almeno uno è inventato o sbagliato."
    )
    cosa_cambiare: str = Field(
        description="Se non approvata: quale numero è sbagliato e come correggerlo "
        "(con quale tool verificarlo, o toglierlo). Stringa vuota se approvata."
    )


ISTRUZIONI_CRITICO = """Controlli i numeri nelle risposte dell'assistente di OnTheRoad.
Ricevi la domanda, la risposta, i numeri della risposta che non compaiono nelle fonti
e le fonti (risultati dei tool e messaggi dell'utente).

Per ogni numero segnalato decidi:
- è un calcolo corretto fatto con numeri delle fonti (somma, differenza, media,
  conteggio, arrotondamento)? Rifai il calcolo: se torna, va bene;
- altrimenti è inventato o sbagliato.

approvata = true solo se tutti i numeri segnalati vanno bene.
Se non approvata, in cosa_cambiare indica il numero, il valore giusto se è nelle
fonti, oppure di verificarlo con un tool o di toglierlo. Massimo due frasi.
"""

critico = Agent(
    name="Critico dei numeri",
    instructions=ISTRUZIONI_CRITICO,
    model=CONFIG["modello"],
    output_type=Critica,
)


async def valuta(domanda: str, risposta: str, fonti: str) -> Critica | None:
    """None se tutti i numeri hanno una fonte (nessuna chiamata al modello)."""
    sospetti = numeri_senza_fonte(risposta, fonti)
    if not sospetti:
        print("  [critico] numeri tutti nelle fonti")
        return None
    print(f"  [critico] numeri senza fonte: {sorted(sospetti, key=float)}")
    richiesta = (
        f"Domanda: {domanda}\n\nRisposta: {risposta}\n\n"
        f"Numeri senza fonte: {', '.join(sorted(sospetti, key=float))}\n\n"
        f"Fonti:\n{fonti[-CONFIG['critico_max_fonti']:]}"
    )
    critica: Critica = (await Runner.run(critico, richiesta)).final_output
    if critica.approvata:
        print("  [critico] approvata (calcoli corretti)")
    return critica
