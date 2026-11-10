"""Test del chunking dei documenti: niente chiave API, niente Chroma."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from documenti import dividi_in_sezioni, prepara_corpus


def test_sezioni_markdown():
    testo = (
        "# Titolo\n\n## Domanda uno\n\nRisposta uno.\n\n## Domanda due\n\nRisposta due."
    )
    assert dividi_in_sezioni(testo) == [
        ("Domanda uno", "Risposta uno."),
        ("Domanda due", "Risposta due."),
    ]


def test_testo_senza_titoli_una_sezione():
    assert dividi_in_sezioni("Solo testo.\n\nAltro paragrafo.") == [
        ("", "Solo testo.\n\nAltro paragrafo.")
    ]


def test_corpus_id_unici_e_domanda_con_risposta():
    chunk = prepara_corpus()
    ids = [c["id"] for c in chunk]
    assert len(ids) == len(set(ids))
    moto = [c for c in chunk if "moto piccola" in c["testo"]]
    assert len(moto) == 1 and "300cc" in moto[0]["testo"]  # domanda e risposta insieme
    faq = [c for c in chunk if c["source"] == "faq.md"]
    assert len(faq) == 10  # una FAQ = un chunk
