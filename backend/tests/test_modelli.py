"""Test senza chiave API: il JSON rispetta il modello Itinerario."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from pydantic import ValidationError

from config import CONFIG
from modelli import Itinerario, RispostaAgente


def _dati():
    return json.loads(CONFIG["itinerari_json"].read_text(encoding="utf-8"))


def test_tutto_il_json_e_valido():
    itinerari = [Itinerario.model_validate(it) for it in _dati()]
    assert len(itinerari) == 7


def test_km_incoerenti_rifiutati():
    it = _dati()[0]
    it["distance"] += 1
    with pytest.raises(ValidationError, match="distance"):
        Itinerario.model_validate(it)


def test_giorni_incoerenti_rifiutati():
    it = _dati()[0]
    it["days"] += 1
    with pytest.raises(ValidationError, match="days"):
        Itinerario.model_validate(it)


def test_difficolta_sconosciuta_rifiutata():
    it = _dati()[0]
    it["difficulty"] = "Estrema"
    with pytest.raises(ValidationError):
        Itinerario.model_validate(it)


def test_risposta_agente_senza_itinerari():
    r = RispostaAgente(testo="Non ho dati sul Giappone.", itinerari=[])
    assert r.itinerari == []


def test_risposta_agente_richiede_tutti_i_campi():
    with pytest.raises(ValidationError):
        RispostaAgente.model_validate({"testo": "ciao"})
