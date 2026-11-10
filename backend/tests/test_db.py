"""Test senza chiave API: verificano DB e sicurezza di query_db."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from crea_db import crea_db
from strumenti import esegui_select


@pytest.fixture(scope="module", autouse=True)
def db():
    crea_db()


def test_conteggi():
    assert "7" in esegui_select("SELECT COUNT(*) FROM itinerari")
    assert "46" in esegui_select("SELECT COUNT(*) FROM tappe")


def test_km_dolomiti():
    assert "1250" in esegui_select(
        "SELECT km_totali FROM itinerari WHERE id = 'dolomiti-tirolo'"
    )


def test_paese_multiplo():
    out = esegui_select("SELECT id FROM itinerari WHERE paese LIKE '%Austria%'")
    assert "dolomiti-tirolo" in out


@pytest.mark.parametrize("sql", [
    "DELETE FROM itinerari",
    "DROP TABLE tappe",
    "SELECT 1; DROP TABLE tappe",
    "UPDATE itinerari SET prezzo_eur = 0",
])
def test_solo_select(sql):
    assert esegui_select(sql).startswith("Errore")


def test_errore_sql_come_testo():
    assert esegui_select("SELECT colonna_inesistente FROM itinerari").startswith("Errore")
