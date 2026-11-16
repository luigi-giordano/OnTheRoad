"""Modelli Pydantic dell'itinerario, con gli stessi nomi dei campi del frontend
(SAMPLE_ITINERARIES in frontend/app.js), così in M5 l'API li restituisce senza traduzioni.

Il validator rende le regole del punto 1 parte del tipo:
un Itinerario con km o giorni incoerenti non si può costruire.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Tappa(BaseModel):
    name: str
    km: int  # km dalla tappa precedente (0 = partenza)
    hours: str = ""  # testo libero, es. "3h 30m"
    nights: int
    transport: list[str] = []
    notes: str = ""
    photos: list[str] = []


class Itinerario(BaseModel):
    id: str
    title: str
    country: str
    duration: str
    days: int
    distance: int
    difficulty: Literal["Facile", "Media", "Avanzata"]
    season: str
    price: int
    cover: str
    summary: str
    stops: list[Tappa]
    documents: list[str] = []
    vaccinations: list[str] = []
    tips: list[str] = []

    @model_validator(mode="after")
    def coerenza(self):
        km = sum(t.km for t in self.stops)
        if self.distance != km:
            raise ValueError(f"{self.id}: distance {self.distance} ≠ somma tappe {km}")
        notti = sum(t.nights for t in self.stops)
        if self.days != notti + 1:
            raise ValueError(f"{self.id}: days {self.days} ≠ notti {notti} + 1")
        if self.duration != f"{self.days} giorni":
            raise ValueError(
                f"{self.id}: duration '{self.duration}' ≠ '{self.days} giorni'"
            )
        return self


class RispostaAgente(BaseModel):
    """Output strutturato dell'agente: il testo per l'utente e gli id citati.

    L'agente non riscrive i dati degli itinerari: restituisce solo gli id,
    e il codice li carica dal DB con carica_itinerario (dati esatti).
    Nessun valore di default: in strict mode il modello compila sempre tutti i campi.
    """

    testo: str = Field(description="La risposta per l'utente, in italiano.")
    itinerari: list[str] = Field(
        description="Gli id degli itinerari di cui parla la risposta, "
        "es. 'albania-loop'. Lista vuota se la risposta non riguarda un itinerario."
    )
