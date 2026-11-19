"""Test senza chiave API: salvataggio delle richieste su un DB temporaneo."""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from config import CONFIG
from modelli import Richiesta
from strumenti import PREZZI_PACCHETTI, riepilogo_richiesta, salva_richiesta


@pytest.fixture
def db_temporaneo(tmp_path, monkeypatch):
    """Ogni test scrive su un richieste.db nuovo, mai su quello vero."""
    percorso = tmp_path / "richieste.db"
    monkeypatch.setitem(CONFIG, "richieste_db", percorso)
    return percorso


def _richiesta(**cambi):
    dati = {
        "name": "Mario Rossi",
        "email": "mario.rossi@example.com",
        "itinerary_id": "corsica",
        "package": "Completo",
        "message": "",
    }
    dati.update(cambi)
    return Richiesta.model_validate(dati)


def test_salva_e_numera(db_temporaneo):
    assert salva_richiesta(_richiesta()) == 1
    assert salva_richiesta(_richiesta(package="Essenziale")) == 2


def test_prezzo_deciso_dal_codice(db_temporaneo):
    salva_richiesta(_richiesta(package="Su misura"))
    con = sqlite3.connect(db_temporaneo)
    prezzo = con.execute("SELECT prezzo_eur FROM richieste").fetchone()[0]
    con.close()
    assert prezzo == PREZZI_PACCHETTI["Su misura"] == 249


def test_riepilogo_con_titolo_e_prezzo():
    testo = riepilogo_richiesta(_richiesta())
    assert "Corsica" in testo and "€89" in testo


def test_riepilogo_segnala_itinerario_inesistente():
    assert "inesistente" in riepilogo_richiesta(_richiesta(itinerary_id="giappone"))
