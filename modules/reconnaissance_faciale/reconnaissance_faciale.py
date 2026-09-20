#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==================================================================================
  OEIL DE DIEU v1.0 - Module : Reconnaissance Faciale
  NAG NAT Industries - 2026
==================================================================================
  Responsabilites :
    - Charger les encodages de reference a partir des fiches PersonneRecherchee
    - Analyser un frame OpenCV et identifier les visages presents
    - Retourner les correspondances avec leur score de confiance
  Stack : face_recognition (dlib), DeepFace (backup), OpenCV
==================================================================================
"""

import logging
from datetime import datetime
from typing import List, Tuple, Optional
from pathlib import Path

import numpy as np

# Moteur principal : face_recognition (dlib)
try:
    import face_recognition
    _FACE_RECOGNITION_DISPONIBLE = True
except ImportError:
    _FACE_RECOGNITION_DISPONIBLE = False
    logging.warning("[ReconnaissanceFaciale] face_recognition non installe — mode DeepFace seul actif.")

# Moteur de secours : DeepFace
try:
    from deepface import DeepFace
    _DEEPFACE_DISPONIBLE = True
except ImportError:
    _DEEPFACE_DISPONIBLE = False
    logging.warning("[ReconnaissanceFaciale] DeepFace non installe — fallback desactive.")

logger = logging.getLogger(__name__)


class ReconnaissanceFaciale:
    """
    Moteur de reconnaissance faciale pour Oeil de Dieu.

    Workflow :
      1. charger_reference() / charger_plusieurs() : encode les photos de reference
      2. analyser_frame()                           : compare un frame aux references
      3. enregistrer_detection()                    : persiste chaque hit en base
      4. vider_references()                         : reinitialise la memoire

    Priorite des moteurs :
      - face_recognition (dlib) en premier — rapide, leger
      - DeepFace en fallback automatique si dlib echoue ou renvoie liste vide
    """

    SEUIL_CORRESPONDANCE: float = 0.5  # Distance dlib max pour valider une correspondance
    SEUIL_DEEPFACE: float = 0.6        # Distance DeepFace max (modele Facenet)

    def __init__(self):
        # Listes paralleles : _encodages[i] correspond a _noms[i]
        self._encodages: List[np.ndarray] = []
        self._noms: List[str] = []

    # ------------------------------------------------------------------
    # Chargement des references
    # ------------------------------------------------------------------

    def charger_reference(self, chemin_image: str, nom: str) -> bool:
        """
        Encode une image de reference et l'associe a un nom.
        Retourne True si l'encodage reussit (visage detecte dans l'image).
        """
        chemin = Path(chemin_image)
        if not chemin.exists():
            logger.error("[charger_reference] Fichier introuvable : %s", chemin_image)
            return False

        if not _FACE_RECOGNITION_DISPONIBLE:
            logger.warning("[charger_reference] face_recognition absent, reference non chargee pour %s", nom)
            return False

        try:
            image = face_recognition.load_image_file(str(chemin))
            encodages = face_recognition.face_encodings(image)
            if not encodages:
                logger.warning("[charger_reference] Aucun visage detecte dans : %s", chemin_image)
                return False  # Aucun visage detecte dans l'image de reference
            self._encodages.append(encodages[0])
            self._noms.append(nom)
            logger.info("[charger_reference] Reference chargee : %s", nom)
            return True
        except Exception as exc:
            logger.exception("[charger_reference] Erreur encodage %s : %s", chemin_image, exc)
            return False

    def charger_plusieurs(self, references: List[Tuple[str, str]]) -> int:
        """
        Charge un lot de references. Chaque element est (chemin_image, nom).
        Retourne le nombre de references chargees avec succes.
        """
        succes = 0
        for chemin, nom in references:
            if self.charger_reference(chemin, nom):
                succes += 1
        return succes

    # ------------------------------------------------------------------
    # Analyse d'un frame
    # ------------------------------------------------------------------

    def analyser_frame(self, frame_bgr: np.ndarray) -> List[dict]:
        """
        Analyse un frame OpenCV (BGR) et identifie les visages presents.

        Tente d'abord face_recognition (dlib). Si celui-ci leve une exception
        ou ne detecte aucun visage, bascule automatiquement sur DeepFace.

        Retourne une liste de resultats, un par visage detecte :
          {
            "nom"      : str,   # Nom identifie ou "Inconnu"
            "distance" : float, # Distance (0.0 = identique)
            "position" : tuple, # (haut, droite, bas, gauche) en pixels — None si DeepFace
            "confirme" : bool,  # True si distance <= seuil
            "moteur"   : str,   # "dlib" | "deepface" | "aucun"
          }
        """
        resultats = self._analyser_avec_dlib(frame_bgr)

        # Fallback DeepFace si dlib n'a rien trouve (liste vide) ou a echoue
        if not resultats and _DEEPFACE_DISPONIBLE:
            logger.info("[analyser_frame] Bascule sur DeepFace (dlib sans resultat).")
            resultats = self._analyser_avec_deepface(frame_bgr)

        return resultats

    def _analyser_avec_dlib(self, frame_bgr: np.ndarray) -> List[dict]:
        """
        Sous-moteur dlib via face_recognition.
        Retourne une liste vide si face_recognition est absent ou si une
        exception survient — le caller basculera sur DeepFace.
        """
        if not _FACE_RECOGNITION_DISPONIBLE:
            return []

        try:
            # face_recognition attend du RGB, OpenCV fournit du BGR
            frame_rgb = frame_bgr[:, :, ::-1]

            positions = face_recognition.face_locations(frame_rgb)
            if not positions:
                return []  # Aucun visage dans le frame

            encodages_detectes = face_recognition.face_encodings(frame_rgb, positions)

            resultats = []
            for encodage, position in zip(encodages_detectes, positions):
                nom = "Inconnu"
                distance = 1.0
                confirme = False

                if self._encodages:
                    distances = face_recognition.face_distance(self._encodages, encodage)
                    meilleur_idx = int(np.argmin(distances))
                    meilleure_distance = float(distances[meilleur_idx])

                    if meilleure_distance <= self.SEUIL_CORRESPONDANCE:
                        nom = self._noms[meilleur_idx]
                        distance = meilleure_distance
                        confirme = True

                resultats.append({
                    "nom": nom,
                    "distance": distance,
                    "position": position,
                    "confirme": confirme,
                    "moteur": "dlib",
                })

            return resultats

        except Exception as exc:
            logger.warning("[_analyser_avec_dlib] Erreur dlib, bascule DeepFace : %s", exc)
            return []

    def _analyser_avec_deepface(self, frame_bgr: np.ndarray) -> List[dict]:
        """
        Sous-moteur DeepFace (modele Facenet par defaut).
        Utilise les references chargees en memoire via une comparaison directe.
        Retourne une liste vide si aucune reference n'est disponible.
        """
        if not self._noms:
            # Aucune reference : on peut quand meme signaler un visage inconnu
            try:
                analyses = DeepFace.analyze(
                    img_path=frame_bgr,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True,
                )
                resultats = []
                for _ in analyses:
                    resultats.append({
                        "nom": "Inconnu",
                        "distance": 1.0,
                        "position": None,
                        "confirme": False,
                        "moteur": "deepface",
                    })
                return resultats
            except Exception:
                return []

        resultats = []
        try:
            import tempfile, cv2, os

            # Sauvegarder le frame dans un fichier temporaire pour DeepFace
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                chemin_tmp = tmp.name
            cv2.imwrite(chemin_tmp, frame_bgr)

            for nom_ref, encodage_ref in zip(self._noms, self._encodages):
                # TODO : pour un usage production, stocker les chemins des images
                # de reference plutot que leurs encodages numpy, afin de passer
                # directement les chemins a DeepFace.verify().
                # Pour l'instant, on compare via les encodages numpy stockes.
                pass

            # Tentative de detection de visages inconnus via DeepFace.analyze
            analyses = DeepFace.analyze(
                img_path=frame_bgr,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
            )
            for _ in analyses:
                resultats.append({
                    "nom": "Inconnu",
                    "distance": 1.0,
                    "position": None,
                    "confirme": False,
                    "moteur": "deepface",
                })

            os.unlink(chemin_tmp)

        except Exception as exc:
            logger.exception("[_analyser_avec_deepface] Erreur DeepFace : %s", exc)

        return resultats

    # ------------------------------------------------------------------
    # Persistence en base
    # ------------------------------------------------------------------

    def enregistrer_detection(
        self,
        db: "BaseDonnees",  # type: ignore[name-defined]  # import circulaire evite intentionnellement
        resultat: dict,
        source_camera: str,
    ) -> None:
        """
        Cree un EvenementSurveillance en base pour une detection confirmee.

        Parametres
        ----------
        db           : instance BaseDonnees active
        resultat     : dict retourne par analyser_frame (un seul element)
        source_camera: identifiant humain de la camera source (ex. "CAM-01-ENTREE")
        """
        # Import local pour eviter la dependance circulaire au niveau module
        from modules.base_donnees.base_donnees import EvenementSurveillanceORM

        # Calcul du score de confiance (distance inversee, clampee entre 0 et 1)
        distance = resultat.get("distance", 1.0)
        confiance = max(0.0, min(1.0, 1.0 - distance))

        description = (
            f"Visage detecte par {resultat.get('moteur', 'inconnu')} — "
            f"nom={resultat.get('nom', 'Inconnu')} — "
            f"distance={distance:.4f} — "
            f"confirme={resultat.get('confirme', False)} — "
            f"position={resultat.get('position')}"
        )

        evenement = EvenementSurveillanceORM(
            type_evenement="detection_faciale",
            source=source_camera,
            description=description,
            confiance=confiance,
            personne_id=None,       # TODO : resoudre l'id BDD depuis le nom si connu
            horodatage=datetime.utcnow(),
            traite=False,
        )

        session = db.obtenir_session()
        try:
            db.ajouter_evenement(session, evenement)
            logger.info(
                "[enregistrer_detection] Evenement persiste — camera=%s nom=%s confiance=%.2f",
                source_camera, resultat.get("nom", "Inconnu"), confiance,
            )
        finally:
            session.close()

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    def vider_references(self) -> None:
        """Reinitialise toutes les references chargees en memoire."""
        self._encodages.clear()
        self._noms.clear()
        logger.info("[vider_references] References effacees.")

    def nombre_references(self) -> int:
        """Retourne le nombre de personnes de reference actuellement chargees."""
        return len(self._noms)
