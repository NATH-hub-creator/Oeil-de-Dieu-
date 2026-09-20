#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==================================================================================
  OEIL DE DIEU v1.0 - Module : Base de Donnees
  NAG NAT Industries - 2026
==================================================================================
  Responsabilites :
    - Initialiser la base SQLite via SQLAlchemy
    - Definir les modeles ORM (PersonneRecherchee, EvenementSurveillance)
    - Fournir une session et les operations CRUD completes
  Schema physique : voir database/schema.sql

  Chiffrement :
    - Support optionnel SQLCipher via sqlcipher3.
    - Si sqlcipher3 n'est pas installe, bascule silencieusement sur SQLite standard.
    - Pour activer : passer cle_chiffrement="<passphrase>" au constructeur.
==================================================================================
"""

import logging
import os
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    Float,
    event,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


# ----------------------------------------------------------------------------
# Chiffrement SQLCipher (optionnel)
# ----------------------------------------------------------------------------

def _sqlcipher_disponible() -> bool:
    """Retourne True si sqlcipher3 est installe."""
    try:
        import sqlcipher3  # noqa: F401
        return True
    except ImportError:
        return False


def _creer_moteur_chiffre(chemin_db: str, cle: str):
    """
    Cree un moteur SQLAlchemy utilisant SQLCipher.
    La cle est injectee via l'evenement 'connect' pour ne jamais apparaitre
    dans l'URL de connexion (securite).
    """
    from sqlcipher3 import dbapi2 as sqlcipher

    engine = create_engine(
        f"sqlite+pysqlcipher://:{cle}@/{chemin_db}",
        module=sqlcipher,
        echo=False,
    )
    return engine


# ----------------------------------------------------------------------------
# Modeles ORM
# ----------------------------------------------------------------------------

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
    tags = Column(Text, default="")                        # JSON serialise
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
    personne_id = Column(Integer, nullable=True)  # FK optionnel vers PersonneRechercheeORM.id
    horodatage = Column(DateTime, default=datetime.utcnow)
    traite = Column(Boolean, default=False)


# ----------------------------------------------------------------------------
# Facade : BaseDonnees
# ----------------------------------------------------------------------------

class BaseDonnees:
    """
    Facade SQLAlchemy pour Oeil de Dieu.
    Gere la connexion, la creation des tables et les operations CRUD.

    Utilisation typique :
        db = BaseDonnees(cle_chiffrement="mot_de_passe_fort")
        db.initialiser()
        session = db.obtenir_session()
        try:
            personne = db.ajouter_personne(session, PersonneRechercheeORM(...))
        finally:
            session.close()
    """

    def __init__(
        self,
        url: Optional[str] = None,
        cle_chiffrement: Optional[str] = None,
    ):
        """
        Initialise le moteur SQLAlchemy.

        Parametres
        ----------
        url              : URL SQLAlchemy complete. Si None, lit DATABASE_URL depuis
                           l'environnement, ou utilise sqlite:///database/oeil_de_dieu.db.
        cle_chiffrement  : Passphrase SQLCipher. Si fournie ET sqlcipher3 est installe,
                           la base sera chiffree. Sinon, bascule sur SQLite standard.
        """
        database_url = url or os.getenv(
            "DATABASE_URL", "sqlite:///database/oeil_de_dieu.db"
        )

        # Tentative de chiffrement SQLCipher si demande
        if cle_chiffrement and _sqlcipher_disponible():
            # Extraire le chemin du fichier depuis l'URL sqlite:///<chemin>
            chemin_db = database_url.replace("sqlite:///", "").replace("sqlite://", "")
            try:
                self._engine = _creer_moteur_chiffre(chemin_db, cle_chiffrement)
                logger.info("[BaseDonnees] Moteur SQLCipher actif — base chiffree.")
            except Exception as exc:
                logger.warning(
                    "[BaseDonnees] Echec SQLCipher (%s) — bascule SQLite standard.", exc
                )
                self._engine = create_engine(database_url, echo=False)
        else:
            if cle_chiffrement and not _sqlcipher_disponible():
                logger.warning(
                    "[BaseDonnees] sqlcipher3 non installe — base non chiffree."
                    " Installez sqlcipher3 pour activer le chiffrement."
                )
            self._engine = create_engine(database_url, echo=False)

        self._SessionLocal = sessionmaker(
            bind=self._engine, autoflush=True, autocommit=False
        )

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def initialiser(self) -> None:
        """Cree toutes les tables si elles n'existent pas encore."""
        Base.metadata.create_all(self._engine)
        logger.info("[BaseDonnees] Tables initialisees.")

    def obtenir_session(self) -> Session:
        """
        Retourne une nouvelle session SQLAlchemy.
        L'appelant est responsable de la fermer (session.close()).
        Preferer un bloc try/finally ou un context manager.
        """
        return self._SessionLocal()

    # ------------------------------------------------------------------
    # CRUD — PersonneRecherchee
    # ------------------------------------------------------------------

    def ajouter_personne(
        self, session: Session, personne: PersonneRechercheeORM
    ) -> PersonneRechercheeORM:
        """Persiste une nouvelle personne et retourne l'objet avec son id affecte."""
        session.add(personne)
        session.commit()
        session.refresh(personne)
        return personne

    def obtenir_personne(
        self, session: Session, id_personne: int
    ) -> Optional[PersonneRechercheeORM]:
        """
        Retourne la PersonneRechercheeORM dont l'id correspond, ou None.

        Parametres
        ----------
        session     : session SQLAlchemy active
        id_personne : cle primaire de la personne recherchee
        """
        return session.get(PersonneRechercheeORM, id_personne)

    def lister_personnes(
        self,
        session: Session,
        statut: Optional[str] = None,
    ) -> List[PersonneRechercheeORM]:
        """
        Retourne la liste des personnes, avec filtre optionnel par statut.

        Parametres
        ----------
        session : session SQLAlchemy active
        statut  : "active" | "suspendue" | "cloturee" | None (toutes)
        """
        requete = session.query(PersonneRechercheeORM)
        if statut is not None:
            requete = requete.filter_by(statut=statut)
        return requete.order_by(PersonneRechercheeORM.date_creation.desc()).all()

    def lister_personnes_actives(
        self, session: Session
    ) -> List[PersonneRechercheeORM]:
        """Raccourci : retourne toutes les personnes dont le statut est 'active'."""
        return self.lister_personnes(session, statut="active")

    def mettre_a_jour_personne(
        self, session: Session, id_personne: int, **kwargs: Any
    ) -> Optional[PersonneRechercheeORM]:
        """
        Met a jour les champs indiques sur une personne existante (update partiel).

        Seuls les champs declares dans PersonneRechercheeORM sont acceptes ;
        les cles inconnues sont ignorees avec un avertissement.

        Retourne l'objet mis a jour, ou None si la personne n'existe pas.

        Exemple
        -------
        db.mettre_a_jour_personne(session, 42, statut="suspendue", alias="Alias2")
        """
        personne = session.get(PersonneRechercheeORM, id_personne)
        if personne is None:
            logger.warning(
                "[mettre_a_jour_personne] Personne id=%d introuvable.", id_personne
            )
            return None

        colonnes_valides = {c.key for c in PersonneRechercheeORM.__table__.columns}
        for champ, valeur in kwargs.items():
            if champ in colonnes_valides:
                setattr(personne, champ, valeur)
            else:
                logger.warning(
                    "[mettre_a_jour_personne] Champ inconnu ignore : %s", champ
                )

        # Forcer la mise a jour de la date
        personne.date_mise_a_jour = datetime.utcnow()
        session.commit()
        session.refresh(personne)
        return personne

    def supprimer_personne(
        self, session: Session, id_personne: int
    ) -> bool:
        """
        Suppression logique : passe le statut a 'cloturee' sans supprimer la ligne.
        Retourne True si la personne existait, False sinon.

        Note : aucune ligne n'est physiquement supprimee — les evenements associes
        restent integres pour audit.
        """
        personne = session.get(PersonneRechercheeORM, id_personne)
        if personne is None:
            logger.warning(
                "[supprimer_personne] Personne id=%d introuvable.", id_personne
            )
            return False

        personne.statut = "cloturee"
        personne.date_mise_a_jour = datetime.utcnow()
        session.commit()
        logger.info("[supprimer_personne] Personne id=%d marquee 'cloturee'.", id_personne)
        return True

    # ------------------------------------------------------------------
    # CRUD — EvenementSurveillance
    # ------------------------------------------------------------------

    def ajouter_evenement(
        self, session: Session, evenement: EvenementSurveillanceORM
    ) -> EvenementSurveillanceORM:
        """
        Persiste un nouvel evenement de surveillance et retourne l'objet avec son id.
        """
        session.add(evenement)
        session.commit()
        session.refresh(evenement)
        return evenement

    # Alias maintenu pour compatibilite avec le code existant
    def enregistrer_evenement(
        self, session: Session, evenement: EvenementSurveillanceORM
    ) -> EvenementSurveillanceORM:
        """Alias de ajouter_evenement — conserve pour compatibilite."""
        return self.ajouter_evenement(session, evenement)

    def lister_evenements_non_traites(
        self,
        session: Session,
        limit: int = 50,
    ) -> List[EvenementSurveillanceORM]:
        """
        Retourne les evenements non encore marques comme traites.
        Tries par horodatage decroissant (les plus recents en premier).

        Parametres
        ----------
        session : session SQLAlchemy active
        limit   : nombre maximum de resultats (defaut : 50)
        """
        return (
            session.query(EvenementSurveillanceORM)
            .filter_by(traite=False)
            .order_by(EvenementSurveillanceORM.horodatage.desc())
            .limit(limit)
            .all()
        )

    def marquer_traite(self, session: Session, evenement_id: int) -> bool:
        """
        Passe le champ traite a True sur l'evenement indique.
        Retourne True si l'evenement existait, False sinon.

        Parametres
        ----------
        session      : session SQLAlchemy active
        evenement_id : cle primaire de l'evenement a marquer
        """
        evenement = session.get(EvenementSurveillanceORM, evenement_id)
        if evenement is None:
            logger.warning(
                "[marquer_traite] Evenement id=%d introuvable.", evenement_id
            )
            return False

        evenement.traite = True
        session.commit()
        logger.info("[marquer_traite] Evenement id=%d marque traite.", evenement_id)
        return True
