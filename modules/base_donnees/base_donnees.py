#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Module : Base de Donnees
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Initialiser la base SQLite via SQLAlchemy
    - Definir les modeles ORM (PersonneRecherchee, EvenementSurveillance)
    - Fournir une session et les operations CRUD de bas niveau
  Schema physique : voir database/schema.sql
=============================================================================
"""

import os
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    Float,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()


# ---------------------------------------------------------------------------
# Modeles ORM
# ---------------------------------------------------------------------------

class PersonneRechercheeORM(Base):
    """Table des personnes faisant l'objet d'une recherche active."""
    __tablename__ = "personnes_recherchees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False, default="")
    prenom = Column(String(100), nullable=False, default="")
    alias = Column(String(100), default="")
    description = Column(Text, default="")
    statut = Column(String(20), default="active")  # active | suspendue | cloturee
    chemin_photo = Column(String(500), nullable=True)
    derniere_localisation = Column(String(200), nullable=True)
    coordonnees_gps = Column(String(50), nullable=True)   # "lat,lon"
    tags = Column(Text, default="")                        # JSON serialize
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_mise_a_jour = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EvenementSurveillanceORM(Base):
    """Table des evenements detectes lors de la surveillance."""
    __tablename__ = "evenements_surveillance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_evenement = Column(String(50), nullable=False)  # "detection_faciale" | "alerte" | "info"
    source = Column(String(200), default="")
    description = Column(Text, default="")
    confiance = Column(Float, nullable=True)    # Score de confiance 0.0-1.0
    personne_id = Column(Integer, nullable=True)  # FK vers PersonneRechercheeORM.id
    horodatage = Column(DateTime, default=datetime.utcnow)
    traite = Column(Boolean, default=False)


# ---------------------------------------------------------------------------
# Gestionnaire de base de donnees
# ---------------------------------------------------------------------------

class BaseDonnees:
    """
    Facade SQLAlchemy pour Oeil de Dieu.
    Gere la connexion, la creation des tables et les operations CRUD.
    """

    def __init__(self, url: Optional[str] = None):
        """
        Initialise le moteur SQLAlchemy.
        Si url est None, lit DATABASE_URL depuis l'environnement.
        Defaut : SQLite local.
        """
        database_url = url or os.getenv("DATABASE_URL", "sqlite:///database/oeil_de_dieu.db")
        self._engine = create_engine(database_url, echo=False)
        self._SessionLocal = sessionmaker(bind=self._engine, autoflush=True, autocommit=False)

    def initialiser(self) -> None:
        """Cree toutes les tables si elles n'existent pas encore."""
        Base.metadata.create_all(self._engine)

    def obtenir_session(self) -> Session:
        """Retourne une session SQLAlchemy. L'appelant doit la fermer."""
        return self._SessionLocal()

    # --- Personnes recherchees ---

    def ajouter_personne(self, session: Session, personne: PersonneRechercheeORM) -> PersonneRechercheeORM:
        """Persiste une nouvelle personne et retourne l'objet avec son id."""
        session.add(personne)
        session.commit()
        session.refresh(personne)
        return personne

    def lister_personnes_actives(self, session: Session) -> List[PersonneRechercheeORM]:
        """Retourne toutes les personnes dont le statut est 'active'."""
        return session.query(PersonneRechercheeORM).filter_by(statut="active").all()

    def obtenir_personne(self, session: Session, id_personne: int) -> Optional[PersonneRechercheeORM]:
        """Retourne la personne correspondant a l'id, ou None."""
        return session.get(PersonneRechercheeORM, id_personne)

    # --- Evenements de surveillance ---

    def enregistrer_evenement(self, session: Session, evenement: EvenementSurveillanceORM) -> EvenementSurveillanceORM:
        """Persiste un evenement de surveillance."""
        session.add(evenement)
        session.commit()
        session.refresh(evenement)
        return evenement

    def lister_evenements_non_traites(self, session: Session) -> List[EvenementSurveillanceORM]:
        """Retourne les evenements pas encore marques comme traites."""
        return session.query(EvenementSurveillanceORM).filter_by(traite=False).all()
