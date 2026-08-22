#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Gold Code Validator
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Valider un Gold Code TOTP fourni par l'utilisateur
    - Verifier la coherence du secret configure
    - Journaliser les tentatives de validation (succes/echec)
=============================================================================
"""

import os
import time
import pyotp
from datetime import datetime
from typing import Tuple


class GoldCodeValidator:
    """
    Validateur du Gold Code TOTP pour Oeil de Dieu.
    Separe du generateur pour respecter le principe de responsabilite unique.
    Le validateur est cote serveur ; le generateur peut etre cote client (app).
    """

    # Nombre de fenetres temporelles tolerees de chaque cote
    # valid_window=1 tolere la fenetre precedente et la suivante
    VALID_WINDOW: int = 1

    def __init__(self):
        secret = os.getenv("GOLD_CODE_SECRET", "")
        if not secret:
            raise EnvironmentError(
                "GOLD_CODE_SECRET absent du fichier .env."
            )
        self._intervalle: int = int(os.getenv("GOLD_CODE_INTERVAL", 300))
        self._totp = pyotp.TOTP(secret, interval=self._intervalle)
        self._journal: list = []

    def valider(self, code_fourni: str) -> Tuple[bool, str]:
        """
        Valide un code TOTP fourni par l'utilisateur.

        Retourne :
            (True, "Gold Code valide.")    si le code est correct
            (False, <raison>)              si invalide ou malformé

        La validation est insensible aux espaces (pratique sur mobile).
        """
        code_nettoye = code_fourni.strip().replace(" ", "")

        if not code_nettoye.isdigit() or len(code_nettoye) != 6:
            self._journaliser(code_nettoye, False, "Format invalide")
            return False, "Le Gold Code doit comporter exactement 6 chiffres."

        resultat = self._totp.verify(code_nettoye, valid_window=self.VALID_WINDOW)

        if resultat:
            self._journaliser(code_nettoye, True, "OK")
            return True, "Gold Code valide."
        else:
            self._journaliser(code_nettoye, False, "Code incorrect ou expire")
            return False, "Gold Code incorrect ou expire. Verifiez l'heure de votre appareil."

    def _journaliser(self, code: str, succes: bool, motif: str) -> None:
        """
        Enregistre une tentative de validation dans le journal interne.
        Le code est masque pour ne jamais apparaitre en clair dans les logs.
        """
        entree = {
            "horodatage": datetime.now().isoformat(),
            "code_masque": "***" + code[-2:] if len(code) >= 2 else "***",
            "succes": succes,
            "motif": motif,
        }
        self._journal.append(entree)
        # Limiter la taille du journal en memoire
        if len(self._journal) > 100:
            self._journal.pop(0)

    def journal(self) -> list:
        """Retourne une copie du journal des validations."""
        return list(self._journal)

    def reinitialiser_journal(self) -> None:
        """Vide le journal des validations."""
        self._journal.clear()

    def taux_echec_recent(self, n: int = 10) -> float:
        """
        Calcule le taux d'echec sur les n derniers tentatives.
        Utile pour detecter une attaque par force brute.
        Retourne un float entre 0.0 (aucun echec) et 1.0 (tous echoues).
        """
        if not self._journal:
            return 0.0
        recents = self._journal[-n:]
        echecs = sum(1 for e in recents if not e["succes"])
        return echecs / len(recents)
