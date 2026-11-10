"""Ricerca nei documenti (FAQ, pacchetti, guide e normative in corpus/).

TODO (primo passo della prossima sessione):
porta qui documenti.py dell'assistente di M3·L12 (indicizzazione del corpus nel
vector DB + recupera) e adatta i percorsi a CONFIG['corpus_dir'] e
CONFIG['collection']. Il contratto da rispettare è quello di cerca():
restituisce i chunk già formattati con [id] davanti, così l'agente può citarli.
"""
from config import CONFIG


def indicizza() -> None:
    raise NotImplementedError("Collega qui l'indicizzazione di M3·L12.")


def cerca(domanda: str, k: int = CONFIG["k"]) -> str:
    raise NotImplementedError("Collega qui il recupera() di M3·L12.")
