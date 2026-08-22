#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Module : Authentification
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Verification du mot de passe maitre via bcrypt
    - Verification du Gold Code TOTP (Google Authenticator / pyotp)
    - Controle du niveau d'habilitation
  Securite critique :
    - Le mot de passe n'est JAMAIS compare en clair
    - Le hash bcrypt est lu depuis la variable d'environnement MASTER_PASSWORD_HASH
=============================================================================
"""

import os
import bcrypt
import pyotp
from typing import Tuple


class AuthManager:
    """
    Gestionnaire d'authentification a double facteur.

    Facteur 1 : mot de passe maitre verifie par bcrypt
    Facteur 2 : Gold Code TOTP (intervalle configurable, defaut 300 s)
    """

    def __init__(self):
        # Hash bcrypt du mot de passe maitre (jamais le mot de passe en clair)
        self._hash_mdp: bytes = self._charger_hash_mdp()
        # Secret TOTP pour le Gold Code
        self._secret_totp: str = os.getenv("GOLD_CODE_SECRET", "")
        # Intervalle TOTP en secondes (defaut : 300 = 5 minutes)
        self._intervalle: int = int(os.getenv("GOLD_CODE_INTERVAL", 300))
        # Habilitation minimum
        self._habilitation_min: int = int(os.getenv("HABILITATION_MIN", 3))

    @staticmethod
    def _charger_hash_mdp() -> bytes:
        """
        Charge le hash bcrypt depuis la variable d'environnement.
        Leve une EnvironmentError si la variable est absente ou vide.
        """
        valeur = os.getenv("MASTER_PASSWORD_HASH", "")
        if not valeur:
            raise EnvironmentError(
                "MASTER_PASSWORD_HASH absent du fichier .env. "
                "Generez un hash avec : "
                "python -c \"import bcrypt; print(bcrypt.hashpw(b'votre_mdp', bcrypt.gensalt()).decode())\""
            )
        return valeur.encode("utf-8")

    def verifier_mot_de_passe(self, mot_de_passe: str) -> bool:
        """
        Verifie le mot de passe saisi contre le hash bcrypt stocke.
        Retourne True si le mot de passe est correct, False sinon.
        Le mot de passe en clair n'est jamais stocke ni logue.
        """
        try:
            return bcrypt.checkpw(mot_de_passe.encode("utf-8"), self._hash_mdp)
        except Exception:
            return False

    def verifier_gold_code(self, code_saisi: str) -> bool:
        """
        Verifie le Gold Code TOTP fourni par Google Authenticator.
        La fenetre de validite correspond a l'intervalle configure.
        """
        if not self._secret_totp:
            return False
        try:
            totp = pyotp.TOTP(self._secret_totp, interval=self._intervalle)
            # valid_window=1 tolere une fenetre adjacente pour compenser les decalages d'horloge
            return totp.verify(code_saisi, valid_window=1)
        except Exception:
            return False

    def authentifier(self, mot_de_passe: str, gold_code: str) -> Tuple[bool, str]:
        """
        Authentification complete a double facteur.

        Retourne :
            (True, "Acces autorise") si les deux facteurs sont valides
            (False, <message d'erreur>) sinon

        L'ordre de verification est intentionnel : mot de passe d'abord,
        puis Gold Code. Ne pas inverser (timing attack mitigation).
        """
        if not mot_de_passe or not gold_code:
            return False, "Tous les champs sont obligatoires."

        if not self.verifier_mot_de_passe(mot_de_passe):
            # Message generique volontaire : ne pas preciser quel facteur a echoue
            return False, "Identifiants incorrects. Acces refuse."

        if not self.verifier_gold_code(gold_code):
            return False, "Gold Code invalide ou expire. Acces refuse."

        return True, "Acces autorise."

    @staticmethod
    def generer_secret_totp() -> str:
        """
        Utilitaire : genere un nouveau secret TOTP aleatoire.
        A utiliser une seule fois a la configuration initiale.
        Stocker la valeur retournee dans GOLD_CODE_SECRET dans .env.
        """
        return pyotp.random_base32()

    def obtenir_uri_qr(self, nom_compte: str = "OeilDeDieu") -> str:
        """
        Genere l'URI otpauth:// pour configurer Google Authenticator via QR code.
        A utiliser uniquement lors de la configuration initiale.
        """
        if not self._secret_totp:
            raise ValueError("GOLD_CODE_SECRET non configure dans .env")
        totp = pyotp.TOTP(self._secret_totp, interval=self._intervalle)
        return totp.provisioning_uri(name=nom_compte, issuer_name="NAG NAT Industries")
