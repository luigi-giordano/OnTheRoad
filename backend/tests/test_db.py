"""Test senza chiave API: verificano DB e sicurezza di query_db."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

import sqlite3

from config import CONFIG

from crea_db import crea_db
from strumenti import cerca_nei_testi, esegui_select


@pytest.fixture(scope="module", autouse=True)
def db():
    crea_db()


def test_conteggi():
    assert "7" in esegui_select("SELECT COUNT(*) FROM itinerari")
    assert "46" in esegui_select("SELECT COUNT(*) FROM tappe")


def test_km_dolomiti():
    assert "740" in esegui_select(
        "SELECT km_totali FROM itinerari WHERE id = 'dolomiti-tirolo'"
    )


def test_paese_multiplo():
    out = esegui_select("SELECT id FROM itinerari WHERE paese LIKE '%Austria%'")
    assert "dolomiti-tirolo" in out


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM itinerari",
        "DROP TABLE tappe",
        "SELECT 1; DROP TABLE tappe",
        "UPDATE itinerari SET prezzo_eur = 0",
    ],
)
def test_solo_select(sql):
    assert esegui_select(sql).startswith("Errore")


def test_errore_sql_come_testo():
    assert esegui_select("SELECT colonna_inesistente FROM itinerari").startswith(
        "Errore"
    )


def _righe(sql):
    con = sqlite3.connect(CONFIG["db_path"])
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def test_km_totali_uguali_somma_tappe():
    righe = _righe("""
        SELECT i.id, i.km_totali, SUM(t.km)
        FROM itinerari i JOIN tappe t ON t.itinerario_id = i.id
        GROUP BY i.id
    """)
    for id_, km_totali, somma in righe:
        assert km_totali == somma, f"{id_}: km_totali {km_totali} ≠ somma tappe {somma}"


def test_giorni_uguali_notti_piu_uno():
    righe = _righe("""
        SELECT i.id, i.giorni, SUM(t.notti)
        FROM itinerari i JOIN tappe t ON t.itinerario_id = i.id
        GROUP BY i.id
    """)
    for id_, giorni, notti in righe:
        assert giorni == notti + 1, f"{id_}: {giorni} giorni ma {notti} notti"


def test_cerca_testo_trova_a1_in_due_campi():
    out = cerca_nei_testi("A1")
    assert "tappa: Zagabria" in out
    assert "consiglio" in out


def test_cerca_testo_traghetto_include_turchia():
    assert "Turchia" in cerca_nei_testi("traghett")


def test_cerca_testo_apostrofo_non_rompe_la_query():
    assert not cerca_nei_testi("l'Atlante").startswith("Errore")
