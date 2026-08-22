#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Gold Code Generator
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Generer le Gold Code TOTP renouvele toutes les 5 minutes
    - Fournir l'URI QR code pour la configuration Google Authenticator
    - Calculer le temps restant avant renouvellement
  Algorithme : RFC 6238 (TOTP) via pyotp
  Intervalle  : 300 secondes (5 minutes) - configurable via .env
=============================================================================
"""

import os
import time
import pyotp
import qrcode
from datetime import datetime
from typing import Tuple


class GoldCodeGenerator:
    """
    Generateur de Gold Code TOTP pour Oeil de Dieu.

    Le Gold Code est un mot de passe a usage unique renouvele toutes les
    5 minutes (300 secondes). Il constitue le deuxieme facteur d'authentification
    du systeme, en complement du mot de passe maitre hache en bcrypt.

    Usage :
        gen = GoldCodeGenerator()
        code = gen.code_courant()
        restant = gen.secondes_restantes()
    """

    def __init__(self):
        secret = os.getenv("GOLD_CODE_SECRET", "")
        if not secret:
            raise EnvironmentError(
                "GOLD_CODE_SECRET absent du fichier .env. "
                "Generez un secret avec : python -c \"import pyotp; print(pyotp.random_base32())\""
            )
        self._intervalle: int = int(os.getenv("GOLD_CODE_INTERVAL", 300))
        self._totp = pyotp.TOTP(secret, interval=self._intervalle)

    def code_courant(self) -> str:
        """
        Retourne le Gold Code TOTP valide a cet instant.
        Le code est une chaine de 6 chiffres.
        """
        return self._totp.now()

    def secondes_restantes(self) -> int:
        """
        Retourne le nombre de secondes avant le prochain renouvellement du code.
        Utile pour afficher un compte a rebours dans l'interface.
        """
        return self._intervalle - int(time.time()) % self._intervalle

    def pourcentage_validite(self) -> float:
        """
        Retourne le pourcentage de vie restante du code courant (1.0 = 100%).
        Utile pour une barre de progression dans l'UI.
        """
        return self.secondes_restantes() / self._intervalle

    def horodatage_expiration(self) -> str:
        """
        Retourne l'horodatage ISO 8601 de la prochaine expiration du code.
        """
        ts_expiration = (int(time.time()) // self._intervalle + 1) * self._intervalle
        return datetime.fromtimestamp(ts_expiration).isoformat()

    def uri_provisioning(self, nom_compte: str = "OeilDeDieu") -> str:
        """
        Retourne l'URI otpauth:// pour configurer Google Authenticator.
        A utiliser lors de la configuration initiale uniquement.
        Peut etre encode en QR code avec generer_qr_code().
        """
        return self._totp.provisioning_uri(
            name=nom_compte, issuer_name="NAG NAT Industries"
        )

    def generer_qr_code(self, chemin_sortie: str = "gold_code_qr.png") -> str:
        """
        Genere et sauvegarde le QR code de configuration Google Authenticator.
        ATTENTION : a utiliser lors de la configuration initiale uniquement.
                    Ne pas stocker ce fichier dans le depot Git.
        Retourne le chemin du fichier PNG genere.
        """
        uri = self.uri_provisioning()
        img = qrcode.make(uri)
        img.save(chemin_sortie)
        return chemin_sortie

    def infos(self) -> dict:
        """
        Retourne un dictionnaire avec toutes les informations du code courant.
        Utile pour le debug et l'affichage dans l'UI.
        """
        return {
            "code": self.code_courant(),
            "secondes_restantes": self.secondes_restantes(),
            "pourcentage_validite": self.pourcentage_validite(),
            "expiration": self.horodatage_expiration(),
            "intervalle_secondes": self._intervalle,
        }
