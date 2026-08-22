# Oeil de Dieu v1.0

> **L'Oeil de Dieu est un systeme de surveillance, de detection et d'analyse de haut niveau.**

---

## Informations generales

| Champ | Valeur |
|---|---|
| **Nom** | Oeil de Dieu |
| **Version** | 1.0 |
| **Developpe par** | NAG NAT Industries |
| **Fondateur** | NAGALO Nathanael alias Mr Zero Day |
| **Annee** | 2026 |
| **Contact** | Aucun (raisons de securite) |

---

## Description

Oeil de Dieu est une application de surveillance intelligente, de detection faciale et d'analyse de haut niveau developpee par NAG NAT Industries. Elle integre la reconnaissance faciale, la recherche de personnes, la surveillance camera, la triangulation geographique et la recherche web avancee dans une interface unifiee et securisee.

---

## Acces & Habilitation

**NIVEAU D'HABILITATION MINIMUM REQUIS : 3**

L'acces a ce systeme est strictement reglemente. Tout utilisateur doit disposer d'une habilitation de niveau 3 minimum, valide par le Comite Ethique de NAG NAT Industries. Consultez le fichier `POLITIQUE.md` pour les regles completes d'utilisation.

---

## Stack technologique

- **Interface** : CustomTkinter (theme sombre, animations 3D)
- **Reconnaissance faciale** : face_recognition, DeepFace, OpenCV
- **Base de donnees** : SQLAlchemy + SQLite
- **Securite** : bcrypt (hachage mot de passe), pyotp (2FA Google Authenticator)
- **Gold Code** : TOTP renouvele toutes les 5 minutes (generator_Strap/)
- **Sessions** : Logs JSON chiffres dans user_infos/
- **Cartographie** : Folium, Geopy
- **Analyse** : Pandas, scikit-learn
- **Web** : Requests, BeautifulSoup4

---

## Structure du projet

```
Oeil-de-Dieu/
|-- main.py
|-- requirements.txt
|-- .env.example
|-- README.md
|-- POLITIQUE.md
|-- assets/
|   `-- logo.png
|-- modules/
|   |-- __init__.py
|   |-- auth/
|   |   |-- __init__.py
|   |   `-- auth.py
|   |-- personne_recherchee/
|   |   |-- __init__.py
|   |   `-- personne_recherchee.py
|   |-- recherche_camera/
|   |   |-- __init__.py
|   |   `-- recherche_camera.py
|   |-- reconnaissance_faciale/
|   |   |-- __init__.py
|   |   `-- reconnaissance_faciale.py
|   |-- base_donnees/
|   |   |-- __init__.py
|   |   `-- base_donnees.py
|   |-- recherche_web/
|   |   |-- __init__.py
|   |   `-- recherche_web.py
|   |-- surveillance/
|   |   |-- __init__.py
|   |   `-- surveillance.py
|   `-- triangulation/
|       |-- __init__.py
|       `-- triangulation.py
|-- generator_Strap/
|   |-- __init__.py
|   |-- gold_code_generator.py
|   `-- validator.py
|-- database/
|   `-- schema.sql
|-- security/
|   |-- __init__.py
|   `-- hash_manager.py
|-- user_infos/
|   `-- session_log.py
`-- ui/
    |-- __init__.py
    `-- main_window.py
```

---

## Installation

```bash
# Cloner le depot
git clone https://github.com/NATH-hub-creator/Oeil-de-Dieu-.git
cd Oeil-de-Dieu-

# Creer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Installer les dependances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Editer .env avec vos valeurs

# Lancer l'application
python main.py
```

---

## Securite

- Le mot de passe maitre est TOUJOURS stocke sous forme de hash bcrypt — jamais en clair.
- Le Gold Code TOTP est renouvele automatiquement toutes les 5 minutes.
- Les logs de session sont chiffres en JSON.
- L'acces 2FA via Google Authenticator est obligatoire.

---

## Avertissement legal

Ce systeme est reserve a un usage professionnel autorise. Toute utilisation non autorisee est passible de poursuites judiciaires et de sanctions disciplinaires conformement a la politique de confidentialite de NAG NAT Industries.

---

*NAG NAT Industries -- 2026 -- Tous droits reserves*
