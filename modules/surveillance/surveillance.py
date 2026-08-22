#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Module : Surveillance
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Boucle de surveillance continue sur un flux camera
    - Detection de mouvement par soustraction de fond (OpenCV)
    - Declenchement d'alertes et enregistrement des evenements
    - Interface avec ReconnaissanceFaciale pour identification en temps reel
=============================================================================
"""

import cv2
import threading
import time
from datetime import datetime
from typing import Callable, Optional

from modules.reconnaissance_faciale.reconnaissance_faciale import ReconnaissanceFaciale
from modules.recherche_camera.recherche_camera import RechercheCamera


class Surveillance:
    """
    Moteur de surveillance continue pour Oeil de Dieu.
    Tourne dans un thread dedie, analyse chaque frame en temps reel.
    """

    # Sensibilite de detection de mouvement (surface minimale en pixels)
    SEUIL_MOUVEMENT: int = 1500
    # Cadence d'analyse (frames par seconde cibles)
    FPS_ANALYSE: float = 10.0

    def __init__(
        self,
        camera: RechercheCamera,
        reconnaissance: Optional[ReconnaissanceFaciale] = None,
        callback_alerte: Optional[Callable[[dict], None]] = None,
    ):
        """
        Parametres :
          camera         : source video deja ouverte
          reconnaissance : moteur de reconnaissance faciale (optionnel)
          callback_alerte: fonction appelee a chaque detection, recoit un dict d'evenement
        """
        self._camera = camera
        self._reconnaissance = reconnaissance
        self._callback = callback_alerte
        self._en_cours = False
        self._thread: Optional[threading.Thread] = None
        self._soustracteur = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=False
        )

    def demarrer(self) -> None:
        """
        Lance la boucle de surveillance dans un thread daemon.
        Ne rien faire si la surveillance est deja en cours.
        """
        if self._en_cours:
            return
        self._en_cours = True
        self._thread = threading.Thread(
            target=self._boucle_surveillance, daemon=True, name="Surveillance"
        )
        self._thread.start()

    def arreter(self) -> None:
        """Arrete proprement la boucle de surveillance."""
        self._en_cours = False
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None

    def est_active(self) -> bool:
        """Retourne True si la surveillance est en cours."""
        return self._en_cours

    def _boucle_surveillance(self) -> None:
        """
        Boucle principale (thread dedie) :
          1. Capture un frame
          2. Detecte les mouvements (soustraction de fond)
          3. Si mouvement : lance la reconnaissance faciale
          4. Appelle le callback si une alerte doit etre declenchee
        """
        intervalle = 1.0 / self.FPS_ANALYSE

        while self._en_cours:
            debut = time.monotonic()

            ok, frame = self._camera.capturer_frame()
            if not ok or frame is None:
                time.sleep(0.1)
                continue

            # --- Detection de mouvement ---
            masque = self._soustracteur.apply(frame)
            contours, _ = cv2.findContours(
                masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            mouvement_detecte = any(
                cv2.contourArea(c) >= self.SEUIL_MOUVEMENT for c in contours
            )

            if mouvement_detecte:
                evenement = {
                    "type": "mouvement",
                    "horodatage": datetime.now().isoformat(),
                    "identifications": [],
                }

                # --- Reconnaissance faciale (si moteur charge) ---
                if self._reconnaissance is not None and self._reconnaissance.nombre_references() > 0:
                    identifications = self._reconnaissance.analyser_frame(frame)
                    evenement["identifications"] = identifications
                    evenement["type"] = "detection_faciale" if any(
                        r["confirme"] for r in identifications
                    ) else "mouvement"

                if self._callback is not None:
                    try:
                        self._callback(evenement)
                    except Exception:
                        pass  # Ne jamais planter la boucle de surveillance sur un callback defaillant

            # Cadence cible
            ecart = time.monotonic() - debut
            if ecart < intervalle:
                time.sleep(intervalle - ecart)
