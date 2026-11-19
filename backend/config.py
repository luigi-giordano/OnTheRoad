"""CONFIG unico del progetto (come da M3·L2): tutti i parametri in un posto solo."""
from pathlib import Path

BASE = Path(__file__).parent

CONFIG = {
    # --- dati ---
    "itinerari_json": BASE / "dati" / "itinerari.json",
    "db_path": BASE / "dati" / "itinerari.db",
    "corpus_dir": BASE / "corpus",
    # --- retrieval (da collegare in documenti.py) ---
    "collection": "ontheroad",
    "chunk_size": 500,
    "k": 4,
    # --- agente ---
    # Usa lo stesso modello dell'assistente di M3·L12.
    "modello": "gpt-5.6-luna",
    "max_turns": 10,
    "sessioni_db": BASE / "sessioni.db",
    # --- richieste di pacchetti (M4: scrittura sotto approvazione) ---
    "richieste_db": BASE / "dati" / "richieste.db",
    # --- MCP Trello (M4·L8): token OAuth, fuori da git ---
    "mcp_token_dir": BASE.parent / ".mcp-token",
    "trello_board": "Richieste OnTheRoad",
    "trello_lista_nuove": "Nuove",
    # --- sicurezza query_db (M3·L8) ---
    "limite_righe": 50,
}
