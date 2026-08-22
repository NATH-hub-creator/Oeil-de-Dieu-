#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0
  Systeme de surveillance, de detection et d'analyse de haut niveau
=============================================================================
  Developpe par : NAG NAT Industries
  Fondateur     : NAGALO Nathanael alias Mr Zero Day
  Annee         : 2026
  Contact       : Aucun (raisons de securite)
  Habilitation  : Niveau >= 3 requis
=============================================================================
"""

import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement AVANT tout autre import
load_dotenv()

# Verifier le niveau d'habilitation minimum au demarrage
HABILITATION_MIN = int(os.getenv("HABILITATION_MIN", 3))


def verifier_environnement() -> bool:
    """Verifie que les variables critiques sont presentes dans .env."""
    variables_requises = [
        "MASTER_PASSWORD_HASH",
        "GOLD_CODE_SECRET",
        "SESSION_ENCRYPTION_KEY",
    ]
    manquantes = [v for v in variables_requises if not os.getenv(v)]
    if manquantes:
        print("[ERREUR CRITIQUE] Variables d'environnement manquantes :")
        for v in manquantes:
            print(f"  - {v}")
        print("Copiez .env.example en .env et renseignez toutes les valeurs.")
        return False
    return True


def main() -> None:
    """
    Point d'entree principal du systeme Oeil de Dieu.
    Effectue les verifications de securite puis lance l'interface.
    """
    print("=" * 60)
    print("  OEIL DE DIEU v1.0 - NAG NAT Industries")
    print("  Systeme de surveillance et d'analyse de haut niveau")
    print("=" * 60)
    print(f"  Habilitation minimum requise : Niveau {HABILITATION_MIN}")
    print("=" * 60)

    # Verification de l'environnement avant lancement
    if not verifier_environnement():
        sys.exit(1)

    # Import de l'interface uniquement apres validation de l'environnement
    try:
        from ui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except ImportError as e:
        print(f"[ERREUR] Impossible de charger l'interface : {e}")
        print("Verifiez que toutes les dependances sont installees : pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[ERREUR CRITIQUE] Erreur inattendue au lancement : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
