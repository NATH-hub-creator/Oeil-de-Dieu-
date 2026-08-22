#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Logs de session
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Enregistrer chaque session utilisateur dans un fichier JSON chiffre
    - Stocker : nom, prenom, ID operateur, date, heure de connexion
    - Signer chaque entree avec HMAC-SHA256 pour garantir l'integrite
    - Detecter toute modification frauduleuse du fichier de logs
=============================================================================
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from security.hash_manager import HashManager

# Dossier de stockage des logs (cree automatiquement si absent)
DOSSIER_LOGS = Path("user_infos")
FICHIER_LOGS = DOSSIER_LOGS / "sessions.json"


class SessionLog:
    """
    Gestionnaire de logs de session pour Oeil de Dieu.

    Chaque entree contient :
      - id_operateur : identifiant unique de l'operateur
      - nom / prenom : identite de l'operateur
      - date_connexion : date ISO 8601
      - heure_connexion : heure locale HH:MM:SS
      - signature HMAC-SHA256 : garantit l'integrite de l'entree

    Le fichier JSON est stocke localement. Pour un deploiement securise,
    remplacer par un stockage en base de donnees chiffree.
    """

    def __init__(self, chemin: Optional[Path] = None):
        self._chemin = chemin or FICHIER_LOGS
        self._chemin.parent.mkdir(parents=True, exist_ok=True)
        self._hash_manager = HashManager()

    def enregistrer(self, id_operateur: str, nom: str, prenom: str) -> dict:
        """
        Cree et persiste une nouvelle entree de session.

        Parametres :
          id_operateur : identifiant unique (ex. "OP-0042")
          nom          : nom de famille de l'operateur
          prenom       : prenom de l'operateur

        Retourne le dictionnaire de l'entree creee.
        """
        maintenant = datetime.now()
        entree = {
            "id_operateur": id_operateur,
            "nom": nom,
            "prenom": prenom,
            "date_connexion": maintenant.strftime("%Y-%m-%d"),
            "heure_connexion": maintenant.strftime("%H:%M:%S"),
            "horodatage_iso": maintenant.isoformat(),
        }
        # Signer l'entree pour detecter toute alteration ulterieure
        contenu_signe = json.dumps(entree, ensure_ascii=False, sort_keys=True)
        entree["signature"] = HashManager.hmac_sha256(contenu_signe)

        sessions = self._charger_sessions()
        sessions.append(entree)
        self._sauvegarder_sessions(sessions)
        return entree

    def verifier_integrite(self) -> bool:
        """
        Verifie la signature HMAC de chaque entree du fichier de logs.
        Retourne True si toutes les entrees sont integres, False sinon.
        """
        sessions = self._charger_sessions()
        for entree in sessions:
            signature = entree.pop("signature", None)
            if signature is None:
                return False
            contenu = json.dumps(entree, ensure_ascii=False, sort_keys=True)
            if not HashManager.verifier_integrite(contenu, signature):
                return False
            entree["signature"] = signature  # Restaurer
        return True

    def lister_sessions(self) -> List[dict]:
        """Retourne toutes les entrees de session."""
        return self._charger_sessions()

    def sessions_du_jour(self) -> List[dict]:
        """Retourne les sessions de la journee courante."""
        aujourd_hui = datetime.now().strftime("%Y-%m-%d")
        return [
            s for s in self._charger_sessions()
            if s.get("date_connexion") == aujourd_hui
        ]

    def _charger_sessions(self) -> List[dict]:
        """Charge et retourne les sessions depuis le fichier JSON."""
        if not self._chemin.exists():
            return []
        try:
            with open(self._chemin, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _sauvegarder_sessions(self, sessions: List[dict]) -> None:
        """Sauvegarde la liste des sessions dans le fichier JSON."""
        with open(self._chemin, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
