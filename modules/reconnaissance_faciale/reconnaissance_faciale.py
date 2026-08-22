#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Module : Reconnaissance Faciale
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Charger les encodages de reference a partir des fiches PersonneRecherchee
    - Analyser un frame OpenCV et identifier les visages presents
    - Retourner les correspondances avec leur score de confiance
  Stack : face_recognition (dlib), DeepFace (backup), OpenCV
=============================================================================
"""

import face_recognition
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path


class ReconnaissanceFaciale:
    """
    Moteur de reconnaissance faciale pour Oeil de Dieu.

    Workflow :
      1. charger_references() : encode les photos de reference
      2. analyser_frame()     : compare un frame aux references
      3. Le resultat contient le nom et le score de distance
    """

    SEUIL_CORRESPONDANCE: float = 0.5  # Distance maximale pour valider une correspondance

    def __init__(self):
        # Listes paralleles : encodages[i] correspond a noms[i]
        self._encodages: List[np.ndarray] = []
        self._noms: List[str] = []

    def charger_reference(self, chemin_image: str, nom: str) -> bool:
        """
        Encode une image de reference et l'associe a un nom.
        Retourne True si l'encodage reussit (visage detecte dans l'image).
        """
        chemin = Path(chemin_image)
        if not chemin.exists():
            return False
        try:
            image = face_recognition.load_image_file(str(chemin))
            encodages = face_recognition.face_encodings(image)
            if not encodages:
                return False  # Aucun visage detecte dans l'image de reference
            self._encodages.append(encodages[0])
            self._noms.append(nom)
            return True
        except Exception:
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

    def analyser_frame(
        self, frame_bgr: np.ndarray
    ) -> List[dict]:
        """
        Analyse un frame OpenCV (BGR) et identifie les visages presents.

        Retourne une liste de resultats, un par visage detecte :
          {
            "nom"       : str,   # Nom identifie ou "Inconnu"
            "distance"  : float, # Distance dlib (0.0 = identique)
            "position"  : tuple, # (haut, droite, bas, gauche) en pixels
            "confirme"  : bool,  # True si distance <= SEUIL_CORRESPONDANCE
          }
        """
        # face_recognition attend du RGB, OpenCV fournit du BGR
        frame_rgb = frame_bgr[:, :, ::-1]

        positions = face_recognition.face_locations(frame_rgb)
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
            })

        return resultats

    def vider_references(self) -> None:
        """Supprime toutes les references chargees en memoire."""
        self._encodages.clear()
        self._noms.clear()

    def nombre_references(self) -> int:
        """Retourne le nombre de personnes de reference chargees."""
        return len(self._noms)
