"""Modelli Pydantic dell'itinerario, con gli stessi nomi dei campi del frontend
(SAMPLE_ITINERARIES in frontend/app.js), così in M5 l'API li restituisce senza traduzioni.

Il validator rende le regole del punto 1 parte del tipo:
un Itinerario con km o giorni incoerenti non si può costruire.
"""

from typing import Literal

from pydantic import BaseModel, model_validator


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
