"""Ricerca nei documenti di OnTheRoad: FAQ, pacchetti, chi siamo, guide (RAG).

Offline:  python documenti.py   → indicizza corpus/ nella collection Chroma
Online:   cerca(domanda)        → i k passaggi più simili, con [id] davanti

Pipeline di indicizzazione, tutta con aikit (Modulo 2):
    load (L4) → clean con la ricetta per formato (L5) → sezioni → chunk_recursive (L10)
    → embed (L7) → Chroma (L9)

Perché le sezioni prima del chunking: i documenti in Markdown sono fatti di
sezioni "## titolo" brevi (una domanda FAQ, un pacchetto). chunk_recursive da
solo taglia sul "\\n\\n" e può separare il titolo dal suo testo. Quindi si
divide prima per sezione, e solo le sezioni più lunghe di chunk_size passano
per chunk_recursive. Ogni chunk porta davanti documento e sezione.
"""

from pathlib import Path

from dotenv import load_dotenv

from config import BASE, CONFIG

load_dotenv(BASE.parent / ".env")

from aikit.chunk import chunk_recursive  # noqa: E402
from aikit.clean import clean, pipeline_for  # noqa: E402
from aikit.loaders import load  # noqa: E402

# vectorstore ed embeddings (Chroma, API) si importano dentro le funzioni:
# così i test sul chunking girano senza chiave e senza database.

FORMATI = {".md", ".txt", ".pdf", ".html", ".docx"}


def dividi_in_sezioni(testo: str) -> list[tuple[str, str]]:
    """Divide un testo Markdown sui titoli '#', '##', '###'.

    Restituisce [(titolo, corpo)]. Il testo prima del primo titolo ha titolo "".
    Per i formati senza titoli (PDF, HTML) esce un'unica sezione.
    """
    sezioni, titolo, righe = [], "", []
    for riga in testo.split("\n"):
        if riga.startswith("#"):
            if "\n".join(righe).strip():
                sezioni.append((titolo, "\n".join(righe).strip()))
            titolo, righe = riga.lstrip("#").strip(), []
        else:
            righe.append(riga)
    if "\n".join(righe).strip():
        sezioni.append((titolo, "\n".join(righe).strip()))
    return sezioni


def prepara_chunk(path: Path) -> list[dict]:
    """Un file → lista di chunk {id, testo, source, sezione}. Nessuna chiamata API."""
    if path.suffix.lower() == ".md":
        # il loader di aikit toglie i '#' (e qualche spazio): qui i titoli servono
        # per dividere in sezioni, e il Markdown è già testo
        grezzo = path.read_text(encoding="utf-8")
    else:
        grezzo = "\n".join(d.text for d in load(str(path)))
    pulito = clean(grezzo, pipeline_for(str(path)))

    chunk = []
    for titolo, corpo in dividi_in_sezioni(pulito):
        for pezzo in chunk_recursive(corpo, CONFIG["chunk_size"]):
            if not pezzo.strip():
                continue
            intestazione = f"{path.stem}" + (f" › {titolo}" if titolo else "")
            chunk.append(
                {
                    "id": f"{path.stem}-{len(chunk) + 1:03d}",
                    "testo": f"{intestazione}\n{pezzo.strip()}",
                    "source": path.name,
                    "sezione": titolo,
                }
            )
    return chunk


def prepara_corpus() -> list[dict]:
    file = sorted(
        p for p in CONFIG["corpus_dir"].iterdir() if p.suffix.lower() in FORMATI
    )
    if not file:
        raise FileNotFoundError(f"Nessun documento in {CONFIG['corpus_dir']}")
    tutti = []
    for p in file:
        pezzi = prepara_chunk(p)
        print(f"  {p.name}: {len(pezzi)} chunk")
        tutti.extend(pezzi)
    return tutti


def indicizza() -> None:
    """Ricostruisce da zero la collection (crea_collection cancella e ricrea)."""
    from aikit import vectorstore
    from aikit.embeddings import embed

    chunk = prepara_corpus()
    collection = vectorstore.crea_collection(CONFIG["collection"])
    vectorstore.indicizza(
        collection,
        ids=[c["id"] for c in chunk],
        testi=[c["testo"] for c in chunk],
        embeddings=embed([c["testo"] for c in chunk]),
        metadatas=[{"source": c["source"], "sezione": c["sezione"]} for c in chunk],
    )
    print(
        f"Collection '{CONFIG['collection']}': {collection.count()} chunk indicizzati"
    )


def cerca(domanda: str, k: int = CONFIG["k"]) -> str:
    """I k chunk più simili alla domanda, formattati per l'agente con [id] e score."""
    from aikit import vectorstore

    collection = vectorstore.apri_collection(CONFIG["collection"])
    if collection.count() == 0:
        indicizza()
        collection = vectorstore.apri_collection(CONFIG["collection"])

    risultati = vectorstore.search(collection, domanda, k)
    if not risultati:
        return "Nessun passaggio trovato."
    return "\n\n".join(
        f"[{r['id']}] (score {r['score']:.2f})\n{r['testo']}" for r in risultati
    )


if __name__ == "__main__":
    indicizza()
