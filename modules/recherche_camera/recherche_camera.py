#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Module : Recherche Camera
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Enumerer et ouvrir les flux camera disponibles (USB, IP, RTSP)
    - Capturer des frames pour analyse
    - Gerer l'etat de connexion de chaque source video
=============================================================================
"""

import cv2
from dataclasses import dataclass
from typing import Optional, List, Tuple


@dataclass
class SourceCamera:
    """Representation d'une source video (camera locale ou flux IP)."""
    identifiant: str          # Index entier ("0") ou URL RTSP/HTTP
    nom: str = ""             # Nom affichable
    type_source: str = "usb" # "usb" | "ip" | "rtsp"
    active: bool = False


class RechercheCamera:
    """
    Gestionnaire de sources video pour Oeil de Dieu.
    Detecte les cameras locales, ouvre les flux, capture des frames.
    """

    def __init__(self):
        self._capture: Optional[cv2.VideoCapture] = None
        self._source_courante: Optional[SourceCamera] = None

    def detecter_cameras_locales(self, max_index: int = 8) -> List[SourceCamera]:
        """
        Detecte les cameras USB/V4L connectees en testant les index 0..max_index.
        Retourne la liste des sources disponibles.
        """
        disponibles: List[SourceCamera] = []
        for idx in range(max_index):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                disponibles.append(
                    SourceCamera(
                        identifiant=str(idx),
                        nom=f"Camera locale {idx}",
                        type_source="usb",
                    )
                )
                cap.release()
        return disponibles

    def ouvrir(self, source: SourceCamera) -> bool:
        """
        Ouvre le flux video de la source donnee.
        Ferme le flux precedent si un est deja ouvert.
        Retourne True si l'ouverture reussit.
        """
        self.fermer()
        identifiant = int(source.identifiant) if source.identifiant.isdigit() else source.identifiant
        self._capture = cv2.VideoCapture(identifiant)
        if self._capture.isOpened():
            source.active = True
            self._source_courante = source
            return True
        self._capture = None
        return False

    def capturer_frame(self) -> Tuple[bool, Optional[object]]:
        """
        Capture un frame depuis le flux ouvert.
        Retourne (succes, frame_numpy) ou (False, None) si echec.
        """
        if self._capture is None or not self._capture.isOpened():
            return False, None
        ret, frame = self._capture.read()
        return ret, frame if ret else None

    def fermer(self) -> None:
        """Libere le flux video courant."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        if self._source_courante is not None:
            self._source_courante.active = False
            self._source_courante = None

    def est_ouverte(self) -> bool:
        """Retourne True si un flux est actuellement actif."""
        return self._capture is not None and self._capture.isOpened()

    def proprietes(self) -> dict:
        """
        Retourne les proprietes techniques du flux ouvert
        (resolution, FPS).
        """
        if not self.est_ouverte():
            return {}
        return {
            "largeur": int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "hauteur": int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self._capture.get(cv2.CAP_PROP_FPS),
        }

    def __del__(self):
        """Nettoyage automatique a la destruction de l'objet."""
        self.fermer()
