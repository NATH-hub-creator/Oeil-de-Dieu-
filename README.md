# Oeil de Dieu v1.0

> **L'Oeil de Dieu est un systeme de surveillance, de detection et d'analyse de haut niveau.**

---

## Informations generales

| Champ | Valeur |
|---|---|
| **Nom** | Oeil de Dieu |
| **Version** | 1.0 |
| **Developpe par** | NAG NAT International Foundation Technologies |
| **Fondateur** | NAGALO Williams Nathanael (alias Mr Zero Day) |
| **Annee** | 2026 |
| **Contact** | Aucun (raisons de securite) |

---

## Description

Oeil de Dieu est une application de surveillance intelligente, de detection faciale et d'analyse de haut niveau developpee par NAG NAT International Foundation Technologies. Elle integre la reconnaissance faciale, la recherche de personnes, la surveillance camera, la triangulation geographique et la recherche web avancee dans une interface unifiee et securisee, 100% offline.

---

## Acces & Habilitation

**NIVEAU D'HABILITATION MINIMUM REQUIS : 3**

L'acces a ce systeme est strictement reglemente. Tout utilisateur doit disposer d'une habilitation de niveau 3 minimum, validee par le Comite Ethique de NAG NAT International Foundation Technologies. Consultez le fichier `POLITIQUE.md` pour les regles completes d'utilisation.

---

## Stack technologique

| Composant | Technologie |
|---|---|
| **Interface** | CustomTkinter (theme sombre, dark mode) |
| **Reconnaissance faciale** | face_recognition, DeepFace, OpenCV |
| **Base de donnees** | SQLAlchemy + SQLite (chiffrement SQLCipher optionnel) |
| **Securite** | bcrypt (hachage mot de passe), pyotp (2FA Google Authenticator) |
| **Gold Code** | TOTP renouvele toutes les 60 secondes (generator_Strap/) |
| **Sessions** | Logs JSON chiffres dans user_infos/ |
| **Cartographie** | Folium, Geopy |
| **Analyse** | Pandas, scikit-learn |
| **Web** | Requests, BeautifulSoup4 |

---

## Palette de couleurs (blueprint officiel)

| Element | Code |
|---|---|
| Fond principal | `#0a0a0a` |
| Accent rouge | `#ff0000` |
| Vert terminal | `#00ff41` |
| Texte principal | `#ffffff` |
| Texte secondaire | `#cccccc` |
| Bordures | `#333333` |

---

## Interface — 5 zones (blueprint Sofia/Wixel)

```
+--------------------------------------------------------------+
| HEADER : logo + SYSTEME ACTIF OFFLINE + heure + NIVEAU 5    |
+------+------------------------+-----------------------------+
|  SB  |   ZONE CENTRALE        |   PANNEAU DROIT             |
| SIDE | flux camera simule    | IDENTITE DETECTEE           |
| BAR  | rectangle detection vert| NOM / PRENOM / CNI         |
|  7   | points repere faciaux  | Photo CNI placeholder       |
| icones| SCAN EN COURS...      | AUTORISE / SUSPECT          |
|      | GPS Koudougou          | CONFIRMER ALERTER DOSSIER   |
|      |                        | Historique 3 entrees        |
+------+------------------------+-----------------------------+
| BARRE INF : mini-carte BF | SENTINEL-2A | STABLE | OSINT   |
+--------------------------------------------------------------+
```

---

## Installation

```bash
# Cloner le depot
git clone https://github.com/NATH-hub-creator/Oeil-de-Dieu-.git
cd Oeil-de-Dieu-

# Creer un environnement virtuel
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate        # Windows

# Installer les dependances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Editer .env avec vos valeurs

# Lancer l'application
python main.py
```

---

## Lancement direct (sans .env pour tests UI)

```bash
python -c "from ui.main_window import MainWindow; app = MainWindow(); app.run()"
```

> Note : sans fichier `.env` complet, la page de connexion affichera une erreur DEV — c'est normal. Le tableau de bord est accessible via le code de contournement developeur.

---

## Compilation executable (PyInstaller)

```bash
pyinstaller --onefile --windowed main.py
```

L'executable genere est dans `dist/main` (Linux) ou `dist/main.exe` (Windows). Il peut etre copie sur cle USB et lance directement, sans installation Python.

---

## Modules metier

| Module | Chemin | Statut |
|---|---|---|
| Reconnaissance faciale | `modules/reconnaissance_faciale/reconnaissance_faciale.py` | Complet (dlib + DeepFace fallback) |
| Base de donnees | `modules/base_donnees/base_donnees.py` | Complet (CRUD + SQLCipher optionnel) |
| Authentification | `modules/auth/auth.py` | Scaffold (TODO) |
| Recherche camera | `modules/recherche_camera/recherche_camera.py` | Scaffold (TODO) |
| Recherche web | `modules/recherche_web/recherche_web.py` | Scaffold (TODO) |
| Surveillance | `modules/surveillance/surveillance.py` | Scaffold (TODO) |
| Triangulation | `modules/triangulation/triangulation.py` | Scaffold (TODO) |

---

## Structure du projet

```
Oeil-de-Dieu-/
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
|   |-- personne_recherchee/
|   |-- recherche_camera/
|   |-- reconnaissance_faciale/
|   |-- base_donnees/
|   |-- recherche_web/
|   |-- surveillance/
|   `-- triangulation/
|-- generator_Strap/
|-- database/
|-- security/
|-- user_infos/
`-- ui/
    |-- __init__.py
    `-- main_window.py
```

---

## Securite

- Le mot de passe maitre est TOUJOURS stocke sous forme de hash bcrypt — jamais en clair.
- Le Gold Code TOTP est renouvele automatiquement toutes les 60 secondes.
- Les logs de session sont chiffres en JSON.
- L'acces 2FA via Google Authenticator est obligatoire.

---

## Avertissement legal

Ce systeme est reserve a un usage professionnel autorise. Toute utilisation non autorisee est passible de poursuites judiciaires et de sanctions disciplinaires conformement a la politique de confidentialite de NAG NAT Industries.

---

*NAG NAT International Foundation Technologies -- 2026 -- Tous droits reserves*
