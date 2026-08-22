#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Module : Personne Recherchee
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Creer, lire, mettre a jour et supprimer les fiches de personnes recherchees
    - Lier une fiche a une photo de reference pour la reconnaissance faciale
    - Gerer le statut de recherche (active, suspendue, cloturee)
=============================================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class PersonneRecherchee:
    """
    Fiche d'une personne faisant l'objet d'une recherche active.

    Champs obligatoires : nom, prenom, statut
    Champs optionnels  : alias, description, chemin_photo, coordonnees_gps, tags
    """
    id: Optional[int] = None
    nom: str = ""
    prenom: str = ""
    alias: str = ""
    description: str = ""
    statut: str = "active"           # "active" | "suspendue" | "cloturee"
    chemin_photo: Optional[str] = None   # Chemin vers la photo de reference
    derniere_localisation: Optional[str] = None
    coordonnees_gps: Optional[str] = None   # Format : "lat,lon"
    tags: List[str] = field(default_factory=list)
    date_creation: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    date_mise_a_jour: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def nom_complet(self) -> str:
        """Retourne le nom complet (prenom nom), ou l'alias si les deux sont vides."""
        if self.nom or self.prenom:
            return f"{self.prenom} {self.nom}".strip()
        return self.alias or "Inconnu"

    def est_active(self) -> bool:
        """Retourne True si la recherche est en cours."""
        return self.statut == "active"

    def to_dict(self) -> dict:
        """Serialise la fiche en dictionnaire (pour stockage JSON ou BDD)."""
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "alias": self.alias,
            "description": self.description,
            "statut": self.statut,
            "chemin_photo": self.chemin_photo,
            "derniere_localisation": self.derniere_localisation,
            "coordonnees_gps": self.coordonnees_gps,
            "tags": self.tags,
            "date_creation": self.date_creation,
            "date_mise_a_jour": self.date_mise_a_jour,
        }


class GestionnairePersonnes:
    """
    CRUD en memoire pour les fiches PersonneRecherchee.
    TODO : brancher sur base_donnees.BaseDonnees pour la persistance SQL.
    """

    def __init__(self):
        # Stockage en memoire (remplace par SQLAlchemy Session en production)
        self._fiches: List[PersonneRecherchee] = []
        self._prochain_id: int = 1

    def ajouter(self, fiche: PersonneRecherchee) -> PersonneRecherchee:
        """Ajoute une nouvelle fiche et lui assigne un identifiant unique."""
        fiche.id = self._prochain_id
        self._prochain_id += 1
        self._fiches.append(fiche)
        return fiche

    def obtenir_par_id(self, id_fiche: int) -> Optional[PersonneRecherchee]:
        """Retourne la fiche correspondant a l'identifiant, ou None."""
        return next((f for f in self._fiches if f.id == id_fiche), None)

    def lister_actives(self) -> List[PersonneRecherchee]:
        """Retourne toutes les fiches dont le statut est 'active'."""
        return [f for f in self._fiches if f.est_active()]

    def lister_toutes(self) -> List[PersonneRecherchee]:
        """Retourne toutes les fiches sans filtre de statut."""
        return list(self._fiches)

    def mettre_a_jour_statut(self, id_fiche: int, nouveau_statut: str) -> bool:
        """Change le statut d'une fiche. Retourne True si la fiche existe."""
        fiche = self.obtenir_par_id(id_fiche)
        if fiche is None:
            return False
        fiche.statut = nouveau_statut
        fiche.date_mise_a_jour = datetime.now().isoformat()
        return True

    def supprimer(self, id_fiche: int) -> bool:
        """Supprime une fiche par identifiant. Retourne True si supprimee."""
        avant = len(self._fiches)
        self._fiches = [f for f in self._fiches if f.id != id_fiche]
        return len(self._fiches) < avant

    def rechercher(self, terme: str) -> List[PersonneRecherchee]:
        """
        Recherche textuelle dans nom, prenom, alias et description.
        Insensible a la casse.
        """
        terme_bas = terme.lower()
        return [
            f for f in self._fiches
            if terme_bas in f.nom.lower()
            or terme_bas in f.prenom.lower()
            or terme_bas in f.alias.lower()
            or terme_bas in f.description.lower()
        ]
