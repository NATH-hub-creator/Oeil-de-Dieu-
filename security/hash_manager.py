#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Gestionnaire de hachage et chiffrement
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Hacher les mots de passe avec bcrypt (jamais en clair)
    - Verifier un mot de passe contre son hash bcrypt
    - Chiffrer/dechiffrer des donnees sensibles (cle AES via secret env)
  Regle absolue : aucun mot de passe n'apparait en clair dans ce module.
=============================================================================
"""

import os
import bcrypt
import hashlib
import hmac
from typing import Optional


class HashManager:
    """
    Gestionnaire de securite cryptographique pour Oeil de Dieu.

    Deux responsabilites distinctes :
      1. Hachage bcrypt des mots de passe
      2. HMAC-SHA256 pour l'integrite des donnees sensibles
    """

    # Cout bcrypt (facteur de travail) - augmenter pour ralentir les attaques
    BCRYPT_ROUNDS: int = 12

    @staticmethod
    def hacher_mot_de_passe(mot_de_passe: str) -> str:
        """
        Hache un mot de passe en clair avec bcrypt.
        Retourne le hash encode en UTF-8 (str).
        A stocker dans MASTER_PASSWORD_HASH dans .env.
        Le mot de passe en clair n'est JAMAIS conserve.

        Usage a la configuration initiale uniquement :
            hash = HashManager.hacher_mot_de_passe("mon_mdp_secret")
            # Copier 'hash' dans .env -> MASTER_PASSWORD_HASH=<hash>
        """
        sel = bcrypt.gensalt(rounds=HashManager.BCRYPT_ROUNDS)
        hash_bytes = bcrypt.hashpw(mot_de_passe.encode("utf-8"), sel)
        return hash_bytes.decode("utf-8")

    @staticmethod
    def verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
        """
        Verifie un mot de passe contre son hash bcrypt stocke.
        Retourne True si le mot de passe correspond, False sinon.
        Utilise bcrypt.checkpw qui est resistant aux attaques temporelles.
        """
        try:
            return bcrypt.checkpw(
                mot_de_passe.encode("utf-8"),
                hash_stocke.encode("utf-8"),
            )
        except Exception:
            return False

    @staticmethod
    def hmac_sha256(donnees: str, cle_secrete: Optional[str] = None) -> str:
        """
        Calcule le HMAC-SHA256 de donnees avec une cle secrete.
        Si cle_secrete est None, lit SESSION_ENCRYPTION_KEY depuis .env.
        Retourne le digest hexadecimal.
        Utile pour signer et verifier l'integrite des logs de session.
        """
        cle = cle_secrete or os.getenv("SESSION_ENCRYPTION_KEY", "")
        if not cle:
            raise EnvironmentError(
                "SESSION_ENCRYPTION_KEY absent du fichier .env."
            )
        return hmac.new(
            cle.encode("utf-8"),
            donnees.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def verifier_integrite(donnees: str, signature: str, cle_secrete: Optional[str] = None) -> bool:
        """
        Verifie qu'une signature HMAC-SHA256 correspond aux donnees.
        Utilise hmac.compare_digest pour eviter les attaques temporelles.
        """
        try:
            signature_calculee = HashManager.hmac_sha256(donnees, cle_secrete)
            return hmac.compare_digest(signature_calculee, signature)
        except Exception:
            return False

    @staticmethod
    def sha256(donnees: str) -> str:
        """
        Hash SHA-256 simple (sans cle) pour des donnees non sensibles.
        Ne pas utiliser pour les mots de passe (utiliser bcrypt a la place).
        """
        return hashlib.sha256(donnees.encode("utf-8")).hexdigest()
