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
    # --- sicurezza query_db (M3·L8) ---
    "limite_righe": 50,
}
