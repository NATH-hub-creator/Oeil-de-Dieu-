#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  OEIL DE DIEU v1.0 - Interface principale
  NAG NAT Industries | Country Vision AI — 2026
============================================================
  Framework  : CustomTkinter (dark mode)
  Blueprint  : Maquette officielle Sofia/Wixel
  5 zones    : HEADER / SIDEBAR / ZONE CENTRALE /
               PANNEAU DROIT / BARRE INFERIEURE
  Palette    :
    Fond           #0a0a0a
    Accent rouge   #ff0000
    Vert terminal  #00ff41
    Texte          #ffffff
    Texte 2nd      #cccccc
    Bordures       #333333
  Habilitation minimale : Niveau 3
============================================================
"""

import sys
import platform
import os
import time
import random
import threading

import customtkinter as ctk
from PIL import Image, ImageTk

# --- Imports conditionnels des modules metier ---
try:
    from modules.reconnaissance_faciale.reconnaissance_faciale import MoteurReconnaissanceFaciale
    RECONNAISSANCE_DISPONIBLE = True
except ImportError:
    RECONNAISSANCE_DISPONIBLE = False

try:
    from modules.base_donnees.base_donnees import GestionnaireBaseDonnees
    BASE_DONNEES_DISPONIBLE = True
except ImportError:
    BASE_DONNEES_DISPONIBLE = False

# --- Configuration globale de l'apparence ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# --- Constantes projet ---
APP_NOM = "Oeil de Dieu"
APP_VERSION = "1.0"
APP_EDITEUR = "NAG NAT Industries"
APP_FONDATEUR = "NAGALO Williams Nathanael alias Mr Zero Day"
APP_ANNEE = "2026"
APP_DESCRIPTION = (
    "L'Oeil de Dieu est un systeme de surveillance, de detection "
    "et d'analyse de haut niveau"
)
HABILITATION_MIN = 3

# --- Palette officielle (blueprint Sofia/Wixel) ---
C_FOND       = "#0a0a0a"
C_ROUGE      = "#ff0000"
C_VERT       = "#00ff41"
C_TEXTE      = "#ffffff"
C_TEXTE2     = "#cccccc"
C_BORDURE    = "#333333"
C_PANNEAU    = "#111111"
C_PANNEAU2   = "#0d0d0d"

# Alias compatibilite avec l'ancien code
COULEUR_OR     = "#FFD700"
COULEUR_FOND   = C_FOND
COULEUR_ACCENT = "#1A1A2E"
COULEUR_TEXTE  = C_TEXTE2
COULEUR_DANGER = C_ROUGE
COULEUR_SUCCES = C_VERT


# ============================================================
# COMPOSANT : BoutonAnime (conserve de l'original)
# ============================================================
class BoutonAnime(ctk.CTkButton):
    """Bouton CustomTkinter avec effet 3D au survol et au clic."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._on_entree)
        self.bind("<Leave>", self._on_sortie)
        self.bind("<ButtonPress-1>", self._on_pression)
        self.bind("<ButtonRelease-1>", self._on_relache)
        self._couleur_originale = kwargs.get("fg_color", COULEUR_ACCENT)

    def _on_entree(self, event=None):
        self.configure(border_width=2, border_color=C_VERT)

    def _on_sortie(self, event=None):
        self.configure(border_width=0)

    def _on_pression(self, event=None):
        self.configure(fg_color="#0D0D1A")

    def _on_relache(self, event=None):
        self.configure(fg_color=self._couleur_originale)


# ============================================================
# PAGE : Accueil (conservee, palette adaptee)
# ============================================================
class PageAccueil(ctk.CTkFrame):
    """Page d'accueil : logo en fond, titre, bouton de connexion."""

    def __init__(self, master, callback_connexion, **kwargs):
        super().__init__(master, fg_color=C_FOND, **kwargs)
        self.callback_connexion = callback_connexion
        self._construire()

    def _construire(self):
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(0, weight=1)

        chemin_logo = os.path.join("assets", "logo.png")
        if os.path.exists(chemin_logo):
            try:
                img_brute = Image.open(chemin_logo).convert("RGBA")
                img_brute.putalpha(
                    img_brute.getchannel("A").point(lambda p: int(p * 0.25))
                )
                img_ctk = ctk.CTkImage(
                    light_image=img_brute, dark_image=img_brute, size=(400, 400)
                )
                lbl_logo = ctk.CTkLabel(self, image=img_ctk, text="")
                lbl_logo.grid(row=0, column=0, rowspan=5, sticky="nsew")
                lbl_logo.lower()
            except Exception:
                pass

        ctk.CTkLabel(
            self, text=APP_NOM.upper(),
            font=ctk.CTkFont(family="Helvetica", size=52, weight="bold"),
            text_color=C_VERT,
        ).grid(row=0, column=0, pady=(60, 5), sticky="s")

        ctk.CTkLabel(
            self, text=f"Version {APP_VERSION}  |  {APP_EDITEUR}",
            font=ctk.CTkFont(size=14), text_color=C_TEXTE2,
        ).grid(row=1, column=0, pady=(0, 2))

        ctk.CTkLabel(
            self, text=APP_DESCRIPTION,
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#888888", wraplength=600,
        ).grid(row=2, column=0, pady=(0, 40))

        ctk.CTkLabel(
            self,
            text=f"ACCES RESTREINT - Habilitation niveau {HABILITATION_MIN} minimum requise",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=C_ROUGE,
        ).grid(row=3, column=0, pady=(0, 20))

        BoutonAnime(
            self, text="ACCEDER AU SYSTEME",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COULEUR_ACCENT, hover_color="#16213E",
            text_color=C_VERT, width=280, height=55, corner_radius=8,
            command=self.callback_connexion,
        ).grid(row=4, column=0, pady=(0, 60))

        ctk.CTkLabel(
            self,
            text=f"Fondateur : {APP_FONDATEUR}  |  {APP_ANNEE}  |  Contact : Aucun (raisons de securite)",
            font=ctk.CTkFont(size=9), text_color="#444444",
        ).grid(row=5, column=0, pady=(0, 10), sticky="s")


# ============================================================
# PAGE : Connexion (conservee, palette adaptee)
# ============================================================
class PageConnexion(ctk.CTkFrame):
    """Authentification : mot de passe maitre + Gold Code 2FA."""

    def __init__(self, master, callback_valider, callback_retour, **kwargs):
        super().__init__(master, fg_color=C_FOND, **kwargs)
        self.callback_valider = callback_valider
        self.callback_retour = callback_retour
        self._construire()

    def _construire(self):
        self.grid_rowconfigure(list(range(10)), weight=1)
        self.grid_columnconfigure(0, weight=1)

        chemin_logo = os.path.join("assets", "logo.png")
        if os.path.exists(chemin_logo):
            try:
                img_brute = Image.open(chemin_logo).convert("RGBA")
                img_brute.putalpha(
                    img_brute.getchannel("A").point(lambda p: int(p * 0.12))
                )
                img_ctk = ctk.CTkImage(
                    light_image=img_brute, dark_image=img_brute, size=(300, 300)
                )
                lbl_logo = ctk.CTkLabel(self, image=img_ctk, text="")
                lbl_logo.grid(row=0, column=0, rowspan=10, sticky="nsew")
                lbl_logo.lower()
            except Exception:
                pass

        ctk.CTkLabel(
            self, text="AUTHENTIFICATION",
            font=ctk.CTkFont(size=32, weight="bold"), text_color=C_VERT,
        ).grid(row=0, column=0, pady=(50, 5), sticky="s")

        ctk.CTkLabel(
            self, text=f"Habilitation niveau {HABILITATION_MIN} requise",
            font=ctk.CTkFont(size=12), text_color=C_ROUGE,
        ).grid(row=1, column=0, pady=(0, 30))

        cadre = ctk.CTkFrame(self, fg_color=COULEUR_ACCENT, corner_radius=12, width=420)
        cadre.grid(row=2, column=0, rowspan=5, padx=40, pady=10, sticky="n")
        cadre.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cadre, text="Mot de passe maitre :",
            font=ctk.CTkFont(size=13), text_color=C_TEXTE2,
        ).grid(row=0, column=0, padx=30, pady=(25, 5), sticky="w")

        self.champ_mdp = ctk.CTkEntry(
            cadre, show="*", width=360, height=42, font=ctk.CTkFont(size=14),
            placeholder_text="Saisir le mot de passe...",
        )
        self.champ_mdp.grid(row=1, column=0, padx=30, pady=(0, 15))

        ctk.CTkLabel(
            cadre, text="Gold Code (Google Authenticator) :",
            font=ctk.CTkFont(size=13), text_color=C_TEXTE2,
        ).grid(row=2, column=0, padx=30, pady=(0, 5), sticky="w")

        self.champ_code = ctk.CTkEntry(
            cadre, width=360, height=42, font=ctk.CTkFont(size=14),
            placeholder_text="Code a 6 chiffres...",
        )
        self.champ_code.grid(row=3, column=0, padx=30, pady=(0, 10))

        self.lbl_erreur = ctk.CTkLabel(
            cadre, text="", font=ctk.CTkFont(size=12), text_color=C_ROUGE,
        )
        self.lbl_erreur.grid(row=4, column=0, padx=30, pady=(0, 10))

        BoutonAnime(
            cadre, text="VALIDER",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#0F3460", hover_color="#16213E", text_color=C_VERT,
            width=360, height=48, corner_radius=8, command=self._valider,
        ).grid(row=5, column=0, padx=30, pady=(5, 25))

        BoutonAnime(
            self, text="Retour",
            font=ctk.CTkFont(size=12), fg_color="transparent",
            hover_color="#1A1A2E", text_color="#666666",
            width=100, height=32, command=self.callback_retour,
        ).grid(row=7, column=0, pady=10)

    def _valider(self):
        mdp = self.champ_mdp.get()
        code = self.champ_code.get()
        if not mdp or not code:
            self.lbl_erreur.configure(text="Tous les champs sont obligatoires.")
            return
        self.lbl_erreur.configure(text="")
        self.callback_valider(mdp, code)

    def afficher_erreur(self, message: str):
        self.lbl_erreur.configure(text=message)


# ============================================================
# PAGE : Tableau de bord operationnel — 5 zones blueprint
# ============================================================
class PageDashboard(ctk.CTkFrame):
    """
    Tableau de bord principal Oeil de Dieu.
    5 zones conformes au blueprint officiel Sofia/Wixel :
      1. HEADER  — logo + statut OFFLINE + heure temps reel + niveau securite
      2. SIDEBAR — 7 icones nav + badge alertes dynamique
      3. ZONE CENTRALE (60%) — flux camera + detection + overlay SCAN
      4. PANNEAU DROIT (40%) — fiche identite + boutons AUTORISE/SUSPECT
      5. BARRE INFERIEURE — mini-carte BF + satellite + OSINT
    """

    # Pages de la sidebar
    PAGES_NAV = [
        ("[DB]", "TABLEAU DE BORD"),
        ("[SV]", "SURVEILLANCE"),
        ("[RH]", "RECHERCHE"),
        ("[PS]", "PERSONNES"),
        ("[VH]", "VEHICULES"),
        ("[AL]", "ALERTES"),
        ("[RP]", "RAPPORTS"),
    ]

    # Historique detections simulees
    HISTORIQUE_MOCK = [
        {"heure": "22:17:43", "nom": "KABORE Ibrahim", "statut": "AUTORISE"},
        {"heure": "22:15:09", "nom": "INCONNU #0847",  "statut": "SUSPECT"},
        {"heure": "22:11:31", "nom": "SOME Martial",   "statut": "AUTORISE"},
    ]

    def __init__(self, master, callback_deconnexion, **kwargs):
        super().__init__(master, fg_color=C_FOND, **kwargs)
        self.callback_deconnexion = callback_deconnexion

        # Etat interne
        self._page_active = 0           # index sidebar
        self._nb_alertes = 3            # badge alertes
        self._statut_autorise = True    # bouton AUTORISE/SUSPECT
        self._scan_phase = 0            # animation SCAN EN COURS
        self._actif = True              # flag arret threads

        self._construire()
        self._demarrer_horloges()

    # ----------------------------------------------------------
    # CONSTRUCTION PRINCIPALE
    # ----------------------------------------------------------
    def _construire(self):
        """Assemble les 5 zones dans une grille principale."""
        # Grille : header / corps / footer
        self.grid_rowconfigure(0, weight=0, minsize=60)   # HEADER
        self.grid_rowconfigure(1, weight=1)                # CORPS
        self.grid_rowconfigure(2, weight=0, minsize=70)   # BARRE INF
        self.grid_columnconfigure(0, weight=1)

        self._construire_header()
        self._construire_corps()
        self._construire_barre_inferieure()

    # ----------------------------------------------------------
    # ZONE 1 : HEADER
    # ----------------------------------------------------------
    def _construire_header(self):
        header = ctk.CTkFrame(
            self, fg_color=C_PANNEAU, corner_radius=0,
            border_width=1, border_color=C_BORDURE,
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        # --- Logo + titre (gauche) ---
        bloc_gauche = ctk.CTkFrame(header, fg_color="transparent")
        bloc_gauche.grid(row=0, column=0, padx=(15, 0), pady=8, sticky="w")

        ctk.CTkLabel(
            bloc_gauche,
            text="[ O ]",
            font=ctk.CTkFont(family="Courier", size=22, weight="bold"),
            text_color=C_VERT,
        ).grid(row=0, column=0, padx=(0, 10), rowspan=2)

        ctk.CTkLabel(
            bloc_gauche,
            text="OEIL DE DIEU",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=C_TEXTE,
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            bloc_gauche,
            text="COUNTRY VISION AI  |  NAG NAT Industries",
            font=ctk.CTkFont(size=10),
            text_color=C_TEXTE2,
        ).grid(row=1, column=1, sticky="w")

        # --- Centre : statut OFFLINE ---
        bloc_centre = ctk.CTkFrame(header, fg_color="transparent")
        bloc_centre.grid(row=0, column=1, pady=8)

        ctk.CTkLabel(
            bloc_centre,
            text="SYSTEME ACTIF  —  OFFLINE",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            text_color=C_VERT,
        ).grid(row=0, column=0)

        ctk.CTkLabel(
            bloc_centre,
            text="NIVEAU 5  —  CONFIDENTIEL",
            font=ctk.CTkFont(size=10),
            text_color=C_ROUGE,
        ).grid(row=1, column=0)

        # --- Droite : heure temps reel + bouton deconnexion ---
        bloc_droite = ctk.CTkFrame(header, fg_color="transparent")
        bloc_droite.grid(row=0, column=2, padx=(0, 15), pady=8, sticky="e")

        self.lbl_heure = ctk.CTkLabel(
            bloc_droite,
            text="--:--:--",
            font=ctk.CTkFont(family="Courier", size=18, weight="bold"),
            text_color=C_VERT,
        )
        self.lbl_heure.grid(row=0, column=0, padx=(0, 20))

        self.lbl_date = ctk.CTkLabel(
            bloc_droite,
            text="----/--/--",
            font=ctk.CTkFont(family="Courier", size=10),
            text_color=C_TEXTE2,
        )
        self.lbl_date.grid(row=1, column=0, padx=(0, 20))

        BoutonAnime(
            bloc_droite,
            text="DECONNEXION",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=C_ROUGE, hover_color="#AA2222",
            text_color=C_TEXTE,
            width=110, height=32,
            command=self.callback_deconnexion,
        ).grid(row=0, column=1, rowspan=2)

    # ----------------------------------------------------------
    # CORPS : sidebar + zone centrale + panneau droit
    # ----------------------------------------------------------
    def _construire_corps(self):
        corps = ctk.CTkFrame(self, fg_color="transparent")
        corps.grid(row=1, column=0, sticky="nsew")
        corps.grid_rowconfigure(0, weight=1)
        corps.grid_columnconfigure(0, weight=0, minsize=70)   # SIDEBAR
        corps.grid_columnconfigure(1, weight=6)                # ZONE CENTRALE (~60%)
        corps.grid_columnconfigure(2, weight=4)                # PANNEAU DROIT (~40%)

        self._construire_sidebar(corps)
        self._construire_zone_centrale(corps)
        self._construire_panneau_droit(corps)

    # ----------------------------------------------------------
    # ZONE 2 : SIDEBAR
    # ----------------------------------------------------------
    def _construire_sidebar(self, parent):
        sidebar = ctk.CTkFrame(
            parent, fg_color=C_PANNEAU, corner_radius=0,
            border_width=1, border_color=C_BORDURE,
        )
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_rowconfigure(list(range(len(self.PAGES_NAV) + 2)), weight=0)
        sidebar.grid_rowconfigure(8, weight=1)  # separateur extensible

        self._boutons_nav = []

        for idx, (icone, nom) in enumerate(self.PAGES_NAV):
            # Badge rouge sur Alertes
            est_alertes = (nom == "ALERTES")

            cadre_btn = ctk.CTkFrame(sidebar, fg_color="transparent")
            cadre_btn.grid(row=idx, column=0, pady=2, padx=4, sticky="ew")

            couleur_btn = C_VERT if idx == self._page_active else "transparent"
            btn = ctk.CTkButton(
                cadre_btn,
                text=icone,
                font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
                fg_color=couleur_btn,
                hover_color=C_PANNEAU2,
                text_color=C_TEXTE if idx == self._page_active else C_TEXTE2,
                width=60, height=48, corner_radius=6,
                command=lambda i=idx: self._changer_page(i),
            )
            btn.grid(row=0, column=0)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(text_color=C_VERT))
            btn.bind("<Leave>", lambda e, b=btn, i=idx: b.configure(
                text_color=C_TEXTE if i == self._page_active else C_TEXTE2
            ))
            self._boutons_nav.append(btn)

            # Badge alertes
            if est_alertes:
                self.lbl_badge_alertes = ctk.CTkLabel(
                    cadre_btn,
                    text=str(self._nb_alertes),
                    font=ctk.CTkFont(size=9, weight="bold"),
                    fg_color=C_ROUGE,
                    text_color=C_TEXTE,
                    corner_radius=8,
                    width=18, height=18,
                )
                self.lbl_badge_alertes.grid(row=0, column=1, padx=0)

        # Tooltip text pages
        for idx, (_, nom) in enumerate(self.PAGES_NAV):
            ctk.CTkLabel(
                sidebar,
                text=nom[:3],
                font=ctk.CTkFont(size=7),
                text_color="#444444",
            ).grid(row=len(self.PAGES_NAV) + idx, column=0)

    def _changer_page(self, idx: int):
        """Met a jour la page active dans la sidebar."""
        self._page_active = idx
        for i, btn in enumerate(self._boutons_nav):
            btn.configure(
                fg_color=C_VERT if i == idx else "transparent",
                text_color=C_TEXTE if i == idx else C_TEXTE2,
            )

    # ----------------------------------------------------------
    # ZONE 3 : ZONE CENTRALE — Flux camera simule
    # ----------------------------------------------------------
    def _construire_zone_centrale(self, parent):
        zone = ctk.CTkFrame(
            parent, fg_color=C_PANNEAU, corner_radius=0,
            border_width=1, border_color=C_BORDURE,
        )
        zone.grid(row=0, column=1, sticky="nsew", padx=(0, 1))
        zone.grid_rowconfigure(1, weight=1)
        zone.grid_columnconfigure(0, weight=1)

        # --- Titre de la zone ---
        entete_zone = ctk.CTkFrame(zone, fg_color="#0a0a0a", corner_radius=0)
        entete_zone.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        entete_zone.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            entete_zone,
            text="  FLUX CAMERA — SURVEILLANCE EN COURS",
            font=ctk.CTkFont(family="Courier", size=11, weight="bold"),
            text_color=C_VERT,
        ).grid(row=0, column=0, sticky="w", padx=5, pady=4)

        ctk.CTkLabel(
            entete_zone,
            text="CAM-01  |  KOUDOUGOU — SECTEUR NORD",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color=C_TEXTE2,
        ).grid(row=0, column=1, sticky="e", padx=10)

        # --- Canvas flux camera ---
        self.canvas_camera = ctk.CTkCanvas(
            zone,
            bg="#000000",
            highlightthickness=0,
        )
        self.canvas_camera.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self.canvas_camera.bind("<Configure>", self._redessiner_camera)

        # --- GPS en bas ---
        ctk.CTkLabel(
            zone,
            text="GPS : 12.3647 deg N  |  2.3158 deg W  —  Koudougou, Burkina Faso",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color=C_TEXTE2,
        ).grid(row=2, column=0, sticky="w", padx=8, pady=(0, 4))

    def _redessiner_camera(self, event=None):
        """Redessine le flux camera simule sur le canvas."""
        c = self.canvas_camera
        c.delete("all")
        try:
            w = c.winfo_width()
            h = c.winfo_height()
        except Exception:
            return
        if w < 10 or h < 10:
            return

        # Grille de scan (lignes horizontales)
        for i in range(0, h, 30):
            alpha_val = 20 if i % 60 == 0 else 10
            c.create_line(0, i, w, i, fill="#001a00", width=1)

        # Rectangle de detection visage (vert)
        rx1 = int(w * 0.30)
        ry1 = int(h * 0.15)
        rx2 = int(w * 0.70)
        ry2 = int(h * 0.75)
        c.create_rectangle(rx1, ry1, rx2, ry2, outline=C_VERT, width=2)

        # Coins du rectangle (effet HUD)
        l = 20
        for (x, y, dx, dy) in [
            (rx1, ry1,  l,  0), (rx1, ry1,  0,  l),
            (rx2, ry1, -l,  0), (rx2, ry1,  0,  l),
            (rx1, ry2,  l,  0), (rx1, ry2,  0, -l),
            (rx2, ry2, -l,  0), (rx2, ry2,  0, -l),
        ]:
            c.create_line(x, y, x + dx, y + dy, fill=C_VERT, width=3)

        # Points de repere faciaux (dots verts)
        points_relatifs = [
            (0.50, 0.30), (0.42, 0.38), (0.58, 0.38),
            (0.42, 0.50), (0.58, 0.50), (0.46, 0.58),
            (0.50, 0.60), (0.54, 0.58),
        ]
        cx = (rx1 + rx2) / 2
        cy = (ry1 + ry2) / 2
        fw = rx2 - rx1
        fh = ry2 - ry1
        for (px, py) in points_relatifs:
            x = rx1 + px * fw
            y = ry1 + py * fh
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=C_VERT, outline="")

        # Pourcentage de confiance
        conf = 87 + random.randint(0, 8)
        c.create_text(
            rx1, ry1 - 8,
            text=f"CONFIANCE : {conf}%",
            fill=C_VERT,
            font=("Courier", 10),
            anchor="sw",
        )

        # Overlay SCAN EN COURS anime
        points_scan = ["", ".", "..", "..."]
        texte_scan = "SCAN EN COURS" + points_scan[self._scan_phase % 4]
        c.create_text(
            w // 2, h - 20,
            text=texte_scan,
            fill=C_VERT,
            font=("Courier", 12, "bold"),
        )

        # Ligne de scan horizontale (effet radar)
        y_scan = int((self._scan_phase * 15) % h)
        c.create_line(0, y_scan, w, y_scan, fill="#003300", width=2)

    # ----------------------------------------------------------
    # ZONE 4 : PANNEAU DROIT — Fiche identite
    # ----------------------------------------------------------
    def _construire_panneau_droit(self, parent):
        panneau = ctk.CTkFrame(
            parent, fg_color=C_PANNEAU, corner_radius=0,
            border_width=1, border_color=C_BORDURE,
        )
        panneau.grid(row=0, column=2, sticky="nsew")
        panneau.grid_columnconfigure(0, weight=1)

        # --- Titre ---
        ctk.CTkFrame(
            panneau, fg_color=C_PANNEAU2, corner_radius=0, height=30,
        ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            panneau,
            text="  IDENTITE DETECTEE",
            font=ctk.CTkFont(family="Courier", size=12, weight="bold"),
            text_color=C_VERT,
        ).grid(row=0, column=0, sticky="w", padx=8, pady=4)

        # --- Photo CNI (placeholder) ---
        cadre_photo = ctk.CTkFrame(
            panneau, fg_color="#1a1a1a", corner_radius=4,
            border_width=1, border_color=C_BORDURE,
            width=100, height=130,
        )
        cadre_photo.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        ctk.CTkLabel(
            cadre_photo,
            text="[ PHOTO CNI ]",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color="#555555",
        ).place(relx=0.5, rely=0.5, anchor="center")

        # --- Champs d'identite ---
        champs = [
            ("NOM",              "KABORE"),
            ("PRENOM",           "Ibrahim"),
            ("DATE DE NAISSANCE","14/03/1988"),
            ("NUMERO CNI",       "BF-2026-0847193"),
        ]
        for i, (label, valeur) in enumerate(champs):
            cadre_champ = ctk.CTkFrame(panneau, fg_color="transparent")
            cadre_champ.grid(row=i + 2, column=0, padx=10, pady=1, sticky="ew")
            cadre_champ.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                cadre_champ,
                text=label + " :",
                font=ctk.CTkFont(family="Courier", size=9),
                text_color="#555555",
                width=120, anchor="w",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                cadre_champ,
                text=valeur,
                font=ctk.CTkFont(family="Courier", size=11, weight="bold"),
                text_color=C_TEXTE,
                anchor="w",
            ).grid(row=0, column=1, sticky="w", padx=4)

        # --- Bouton AUTORISE / SUSPECT ---
        self.btn_statut = ctk.CTkButton(
            panneau,
            text="AUTORISE",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=C_VERT, hover_color="#00aa2a",
            text_color="#000000",
            width=180, height=40, corner_radius=6,
            command=self._basculer_statut,
        )
        self.btn_statut.grid(row=6, column=0, padx=20, pady=(12, 6))

        # --- Boutons d'action ---
        boutons_action = [
            ("CONFIRMER",    C_VERT,    "#000000", lambda: None),
            ("ALERTER",      C_ROUGE,   C_TEXTE,   self._declencher_alerte),
            ("VOIR DOSSIER", "#1A1A2E", C_TEXTE,   lambda: None),
        ]
        for j, (txt, couleur_fg, couleur_txt, cmd) in enumerate(boutons_action):
            BoutonAnime(
                panneau,
                text=txt,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=couleur_fg, hover_color="#222222",
                text_color=couleur_txt,
                width=180, height=32, corner_radius=6,
                command=cmd,
            ).grid(row=7 + j, column=0, padx=20, pady=2)

        # --- Separateur ---
        ctk.CTkFrame(
            panneau, fg_color=C_BORDURE, height=1, corner_radius=0,
        ).grid(row=10, column=0, sticky="ew", padx=10, pady=8)

        # --- Historique ---
        ctk.CTkLabel(
            panneau,
            text="  DERNIERES IDENTIFICATIONS",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color="#555555",
        ).grid(row=11, column=0, sticky="w", padx=10)

        for k, entree in enumerate(self.HISTORIQUE_MOCK):
            couleur_statut = C_VERT if entree["statut"] == "AUTORISE" else C_ROUGE
            cadre_h = ctk.CTkFrame(panneau, fg_color="#0d0d0d", corner_radius=4)
            cadre_h.grid(row=12 + k, column=0, padx=10, pady=1, sticky="ew")
            cadre_h.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                cadre_h,
                text=entree["heure"],
                font=ctk.CTkFont(family="Courier", size=9),
                text_color=C_TEXTE2,
            ).grid(row=0, column=0, padx=4, pady=2)

            ctk.CTkLabel(
                cadre_h,
                text=entree["nom"],
                font=ctk.CTkFont(family="Courier", size=9),
                text_color=C_TEXTE2,
            ).grid(row=0, column=1, padx=4, sticky="w")

            ctk.CTkLabel(
                cadre_h,
                text=entree["statut"],
                font=ctk.CTkFont(family="Courier", size=8, weight="bold"),
                text_color=couleur_statut,
            ).grid(row=0, column=2, padx=4)

    def _basculer_statut(self):
        """Alterne le bouton AUTORISE <-> SUSPECT."""
        self._statut_autorise = not self._statut_autorise
        if self._statut_autorise:
            self.btn_statut.configure(
                text="AUTORISE", fg_color=C_VERT,
                hover_color="#00aa2a", text_color="#000000",
            )
        else:
            self.btn_statut.configure(
                text="SUSPECT", fg_color=C_ROUGE,
                hover_color="#aa0000", text_color=C_TEXTE,
            )

    def _declencher_alerte(self):
        """Incremente le compteur d'alertes."""
        self._nb_alertes += 1
        try:
            self.lbl_badge_alertes.configure(text=str(self._nb_alertes))
        except Exception:
            pass

    # ----------------------------------------------------------
    # ZONE 5 : BARRE INFERIEURE — Dashboard OSINT
    # ----------------------------------------------------------
    def _construire_barre_inferieure(self):
        barre = ctk.CTkFrame(
            self, fg_color=C_PANNEAU, corner_radius=0,
            border_width=1, border_color=C_BORDURE,
        )
        barre.grid(row=2, column=0, sticky="ew")
        barre.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # --- Mini-carte textuelle BF ---
        cadre_carte = ctk.CTkFrame(barre, fg_color=C_PANNEAU2, corner_radius=4)
        cadre_carte.grid(row=0, column=0, padx=8, pady=6, sticky="nsew")

        ctk.CTkLabel(
            cadre_carte,
            text="BURKINA FASO — CARTE",
            font=ctk.CTkFont(family="Courier", size=8, weight="bold"),
            text_color="#555555",
        ).grid(row=0, column=0, padx=6, pady=(4, 0))

        ctk.CTkLabel(
            cadre_carte,
            text="[   (*)    ]\n[  / BF \  ]\n[ Koudougou]",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color=C_VERT,
        ).grid(row=1, column=0, padx=6, pady=(0, 4))

        # --- Satellite actif ---
        cadre_sat = ctk.CTkFrame(barre, fg_color=C_PANNEAU2, corner_radius=4)
        cadre_sat.grid(row=0, column=1, padx=4, pady=6, sticky="nsew")

        ctk.CTkLabel(
            cadre_sat,
            text="SATELLITE ACTIF",
            font=ctk.CTkFont(family="Courier", size=8, weight="bold"),
            text_color="#555555",
        ).grid(row=0, column=0, padx=6, pady=(4, 0))

        ctk.CTkLabel(
            cadre_sat,
            text="SENTINEL-2A",
            font=ctk.CTkFont(family="Courier", size=11, weight="bold"),
            text_color=C_TEXTE,
        ).grid(row=1, column=0, padx=6)

        ctk.CTkLabel(
            cadre_sat,
            text="Alt : 786 km  |  Orbite : LEO",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color=C_TEXTE2,
        ).grid(row=2, column=0, padx=6, pady=(0, 4))

        # --- Activite sismique ---
        cadre_seisme = ctk.CTkFrame(barre, fg_color=C_PANNEAU2, corner_radius=4)
        cadre_seisme.grid(row=0, column=2, padx=4, pady=6, sticky="nsew")

        ctk.CTkLabel(
            cadre_seisme,
            text="ACTIVITE SISMIQUE",
            font=ctk.CTkFont(family="Courier", size=8, weight="bold"),
            text_color="#555555",
        ).grid(row=0, column=0, padx=6, pady=(4, 0))

        ctk.CTkLabel(
            cadre_seisme,
            text="STABLE",
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
            text_color=C_VERT,
        ).grid(row=1, column=0, padx=6, pady=(0, 4))

        # --- Statut Ghost OSINT ---
        cadre_osint = ctk.CTkFrame(barre, fg_color=C_PANNEAU2, corner_radius=4)
        cadre_osint.grid(row=0, column=3, padx=(4, 8), pady=6, sticky="nsew")

        ctk.CTkLabel(
            cadre_osint,
            text="GHOST OSINT",
            font=ctk.CTkFont(family="Courier", size=8, weight="bold"),
            text_color="#555555",
        ).grid(row=0, column=0, padx=6, pady=(4, 0))

        ctk.CTkLabel(
            cadre_osint,
            text="Jets trackes : 14",
            font=ctk.CTkFont(family="Courier", size=10),
            text_color=C_TEXTE2,
        ).grid(row=1, column=0, padx=6)

        ctk.CTkLabel(
            cadre_osint,
            text="Alertes actives : 3",
            font=ctk.CTkFont(family="Courier", size=10),
            text_color=C_ROUGE,
        ).grid(row=2, column=0, padx=6, pady=(0, 4))

    # ----------------------------------------------------------
    # HORLOGES ET ANIMATIONS
    # ----------------------------------------------------------
    def _demarrer_horloges(self):
        """Lance les threads d'horloge et d'animation camera."""
        self._maj_heure()
        self._animer_scan()

    def _maj_heure(self):
        """Mise a jour de l'heure toutes les secondes."""
        if not self._actif:
            return
        maintenant = time.localtime()
        self.lbl_heure.configure(
            text=time.strftime("%H:%M:%S", maintenant)
        )
        self.lbl_date.configure(
            text=time.strftime("%Y/%m/%d", maintenant)
        )
        try:
            self.after(1000, self._maj_heure)
        except Exception:
            pass

    def _animer_scan(self):
        """Animation de l'overlay SCAN et de la ligne radar toutes les 200ms."""
        if not self._actif:
            return
        self._scan_phase += 1
        try:
            self._redessiner_camera()
            self.after(200, self._animer_scan)
        except Exception:
            pass

    def destroy(self):
        """Arrete les timers avant destruction du frame."""
        self._actif = False
        super().destroy()


# ============================================================
# CONTROLEUR : MainWindow
# ============================================================
class MainWindow:
    """
    Controleur principal de l'application Oeil de Dieu.
    Gere la navigation entre les pages :
      Accueil -> Connexion -> Dashboard operationnel.
    """

    def __init__(self):
        self.window = ctk.CTk()
        self.window.title(f"{APP_NOM} v{APP_VERSION} - {APP_EDITEUR}")
        self.window.configure(fg_color=C_FOND)

        # Plein ecran selon OS
        os_courant = platform.system()
        if os_courant == "Windows":
            self.window.state("zoomed")
        elif os_courant == "Linux":
            self.window.attributes("-zoomed", True)
        else:
            largeur = self.window.winfo_screenwidth()
            hauteur = self.window.winfo_screenheight()
            self.window.geometry(f"{largeur}x{hauteur}+0+0")

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self._page_courante = None
        self._afficher_accueil()

    def _vider_fenetre(self):
        if self._page_courante is not None:
            self._page_courante.destroy()
            self._page_courante = None

    def _afficher_accueil(self):
        self._vider_fenetre()
        self._page_courante = PageAccueil(
            self.window, callback_connexion=self._afficher_connexion
        )
        self._page_courante.grid(row=0, column=0, sticky="nsew")

    def _afficher_connexion(self):
        self._vider_fenetre()
        self._page_courante = PageConnexion(
            self.window,
            callback_valider=self._valider_identifiants,
            callback_retour=self._afficher_accueil,
        )
        self._page_courante.grid(row=0, column=0, sticky="nsew")

    def _valider_identifiants(self, mot_de_passe: str, gold_code: str):
        """
        Valide le mot de passe (bcrypt) et le Gold Code (TOTP).
        Redirige vers le dashboard operationnel si l'auth reussit.
        """
        try:
            from modules.auth.auth import AuthManager
            auth = AuthManager()
            ok, message = auth.authentifier(mot_de_passe, gold_code)
            if ok:
                self._afficher_dashboard()
            else:
                if isinstance(self._page_courante, PageConnexion):
                    self._page_courante.afficher_erreur(message)
        except ImportError:
            # Fallback DEV : module auth absent
            if isinstance(self._page_courante, PageConnexion):
                self._page_courante.afficher_erreur(
                    "[DEV] Module auth non disponible. Acces temporairement bloque."
                )

    def _afficher_dashboard(self):
        """Affiche le tableau de bord operationnel apres authentification."""
        self._vider_fenetre()
        self._page_courante = PageDashboard(
            self.window, callback_deconnexion=self._afficher_accueil
        )
        self._page_courante.grid(row=0, column=0, sticky="nsew")

    def run(self):
        """Lance la boucle principale de l'interface."""
        self.window.mainloop()
