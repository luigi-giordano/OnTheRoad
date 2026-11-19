"""Test senza rete: la logica delle card con un Trello finto.

Il finto risponde come il server MCP vero (stesse forme JSON viste con
trelloSearch, trelloReadBoard, trelloReadCard), e registra le card create.
"""

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from trello_mcp import crea_card_richiesta, trova_lista

BOARD = "ari:board/1"
NUOVE = "ari:list/nuove"


class TrelloFinto:
    def __init__(self, card=None, board="Richieste OnTheRoad"):
        self.board = board
        self.card = list(card or [])  # card già presenti
        self.create = []  # argomenti delle trelloWriteCard

    async def call_tool(self, tool, argomenti):
        if tool == "trelloSearch":
            dati = {"boards": [{"id": BOARD, "name": self.board}]}
        elif tool == "trelloReadBoard":
            dati = {"id": BOARD, "lists": [{"id": NUOVE, "name": "Nuove"},
                                           {"id": "ari:list/pagate", "name": "Pagate"}]}
        elif tool == "trelloReadCard":
            dati = {"lists": [{"id": NUOVE, "name": "Nuove", "cards": self.card}],
                    "hasNextPage": False, "nextCursor": None}
        elif tool == "trelloWriteCard":
            self.create.append(argomenti)
            nuova = {"id": "ari:card/x", "name": argomenti["name"], "url": "https://trello.com/c/x"}
            self.card.append(nuova)
            dati = nuova
        else:
            raise AssertionError(f"tool inatteso: {tool}")
        return SimpleNamespace(content=[SimpleNamespace(text=json.dumps(dati))], isError=False)


def _crea(trello, numero=1):
    return asyncio.run(crea_card_richiesta(
        trello, numero, "Corsica — L'Isola Selvaggia", "Completo", 89,
        "Mario Rossi", "mario.rossi@example.com", "giugno",
    ))


def test_trova_board_e_lista_per_nome():
    assert asyncio.run(trova_lista(TrelloFinto(), "Richieste OnTheRoad", "Nuove")) == (BOARD, NUOVE)


def test_board_mancante():
    with pytest.raises(RuntimeError, match="non trovata"):
        asyncio.run(trova_lista(TrelloFinto(board="Altro"), "Richieste OnTheRoad", "Nuove"))


def test_crea_card_nella_lista_nuove():
    trello = TrelloFinto()
    esito = _crea(trello)
    assert esito.startswith("card creata")
    (arg,) = trello.create
    assert arg["listId"] == NUOVE
    assert arg["name"] == "#1 · Corsica — L'Isola Selvaggia · Completo · Mario Rossi"
    assert "€89" in arg["desc"] and "mario.rossi@example.com" in arg["desc"]


def test_idempotenza_stessa_richiesta_una_card():
    trello = TrelloFinto()
    _crea(trello)
    esito = _crea(trello)
    assert esito.startswith("card già presente")
    assert len(trello.create) == 1


def test_numero_simile_non_conta_come_duplicato():
    # '#12 ...' non deve bloccare la card della richiesta #1
    trello = TrelloFinto(card=[{"name": "#12 · Albania · Essenziale · Luca"}])
    assert _crea(trello, numero=1).startswith("card creata")
