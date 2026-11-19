"""Test senza chiave API: il livello 1 del critico (estrazione e confronto dei numeri)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from critico import MARCATORE, fonti_dalla_sessione, numeri_nel_testo, numeri_senza_fonte


def test_numeri_in_forma_canonica():
    testo = "Norvegia: 1.140 km in 11 giorni, €109, 5h 30m, 1,5 litri"
    assert numeri_nel_testo(testo) == {"1140", "11", "109", "5", "30", "1.5"}


def test_citazioni_e_numeri_banali_ignorati():
    assert numeri_nel_testo("Vedi [faq-007] e [pacchetti-002]: 2 itinerari, 1 pacchetto") == set()


def test_fonti_solo_tool_e_utente():
    items = [
        {"role": "user", "content": "Ho 7 giorni"},
        {"type": "function_call_output", "call_id": "c1", "output": "Completo €89"},
        {"role": "assistant", "content": [{"type": "output_text", "text": "costa €49"}]},
        {"role": "user", "content": f"{MARCATORE} il 49 è sbagliato"},
    ]
    fonti = fonti_dalla_sessione(items)
    assert "7" in fonti and "89" in fonti
    assert "49" not in fonti  # né la risposta dell'assistente né la revisione contano


def test_numero_inventato_segnalato():
    fonti = "Essenziale €39. Albania Loop 780 km"
    assert numeri_senza_fonte("L'Essenziale costa €49, l'Albania 780 km", fonti) == {"49"}


def test_migliaia_scritte_in_modi_diversi():
    # la fonte ha 1140, la risposta 1.140: è lo stesso numero
    assert numeri_senza_fonte("1.140 km", "km_totali: 1140") == set()


def test_calcolo_segnalato_al_livello_1():
    # 128 = 89 + 39 non è nelle fonti: lo segnala il codice, lo giudica il critico LLM
    assert numeri_senza_fonte("In tutto €128", "Completo €89, Essenziale €39") == {"128"}
