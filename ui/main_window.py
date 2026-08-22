#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Interface principale
  NAG NAT Industries - 2026
=============================================================================
  Fenetre principale CustomTkinter : theme sombre, animations 3D.
  Plein ecran par defaut :
    - Windows : window.state('zoomed')
    - Linux   : window.attributes('-zoomed', True)
  Habilitation minimum : Niveau 3
=============================================================================
"""

import sys
import platform
import os
import customtkinter as ctk
from PIL import Image, ImageTk

# --- Configuration globale de l'apparence ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# --- Constantes projet ---
APP_NOM = "Oeil de Dieu"
APP_VERSION = "1.0"
APP_EDITEUR = "NAG NAT Industries"
APP_FONDATEUR = "NAGALO Nathanael alias Mr Zero Day"
APP_ANNEE = "2026"
APP_DESCRIPTION = "L'Oeil de Dieu est un systeme de surveillance, de detection et d'analyse de haut niveau"
HABILITATION_MIN = 3

# Couleurs de la charte graphique
COULEUR_OR = "#FFD700"
COULEUR_FOND = "#0A0A0A"
COULEUR_ACCENT = "#1A1A2E"
COULEUR_TEXTE = "#E0E0E0"
COULEUR_DANGER = "#FF4444"
COULEUR_SUCCES = "#00AA44"


class BoutonAnimé(ctk.CTkButton):
    """
    Bouton CustomTkinter avec effet 3D au survol et au clic.
    Simule une profondeur visuelle par variation de couleur de bordure.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._on_entree)
        self.bind("<Leave>", self._on_sortie)
        self.bind("<ButtonPress-1>", self._on_pression)
        self.bind("<ButtonRelease-1>", self._on_relache)
        self._couleur_originale = kwargs.get("fg_color", COULEUR_ACCENT)

    def _on_entree(self, event=None):
        """Survol : eclaircissement leger (effet 3D haut)."""
        self.configure(border_width=2, border_color=COULEUR_OR)

    def _on_sortie(self, event=None):
        """Fin survol : retour a l'etat normal."""
        self.configure(border_width=0)

    def _on_pression(self, event=None):
        """Clic : assombrissement (effet 3D enfonce)."""
        self.configure(fg_color="#0D0D1A")

    def _on_relache(self, event=None):
        """Relachement : retour couleur originale."""
        self.configure(fg_color=self._couleur_originale)


class PageAccueil(ctk.CTkFrame):
    """
    Page d'accueil : logo en fond, titre, bouton de connexion.
    """

    def __init__(self, master, callback_connexion, **kwargs):
        super().__init__(master, fg_color=COULEUR_FOND, **kwargs)
        self.callback_connexion = callback_connexion
        self._construire()

    def _construire(self):
        """Construit les widgets de la page d'accueil."""
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Logo (fond de page) ---
        chemin_logo = os.path.join("assets", "logo.png")
        if os.path.exists(chemin_logo):
            try:
                img_brute = Image.open(chemin_logo).convert("RGBA")
                # Semi-transparence : logo utilise comme fond
                img_brute.putalpha(
                    img_brute.getchannel("A").point(lambda p: int(p * 0.25))
                )
                img_ctk = ctk.CTkImage(
                    light_image=img_brute,
                    dark_image=img_brute,
                    size=(400, 400),
                )
                lbl_logo = ctk.CTkLabel(self, image=img_ctk, text="")
                lbl_logo.grid(row=0, column=0, rowspan=5, sticky="nsew")
                lbl_logo.lower()  # Place le logo derriere les autres widgets
            except Exception:
                pass  # Si le logo est absent, on continue sans erreur

        # --- Titre principal ---
        ctk.CTkLabel(
            self,
            text=APP_NOM.upper(),
            font=ctk.CTkFont(family="Helvetica", size=52, weight="bold"),
            text_color=COULEUR_OR,
        ).grid(row=0, column=0, pady=(60, 5), sticky="s")

        # --- Version ---
        ctk.CTkLabel(
            self,
            text=f"Version {APP_VERSION}  |  {APP_EDITEUR}",
            font=ctk.CTkFont(size=14),
            text_color=COULEUR_TEXTE,
        ).grid(row=1, column=0, pady=(0, 2))

        # --- Description ---
        ctk.CTkLabel(
            self,
            text=APP_DESCRIPTION,
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#888888",
            wraplength=600,
        ).grid(row=2, column=0, pady=(0, 40))

        # --- Avertissement habilitation ---
        ctk.CTkLabel(
            self,
            text=f"ACCES RESTREINT - Habilitation niveau {HABILITATION_MIN} minimum requise",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COULEUR_DANGER,
        ).grid(row=3, column=0, pady=(0, 20))

        # --- Bouton connexion (animé 3D) ---
        BoutonAnimé(
            self,
            text="ACCEDER AU SYSTEME",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COULEUR_ACCENT,
            hover_color="#16213E",
            text_color=COULEUR_OR,
            width=280,
            height=55,
            corner_radius=8,
            command=self.callback_connexion,
        ).grid(row=4, column=0, pady=(0, 60))

        # --- Pied de page ---
        ctk.CTkLabel(
            self,
            text=f"Fondateur : {APP_FONDATEUR}  |  {APP_ANNEE}  |  Contact : Aucun (raisons de securite)",
            font=ctk.CTkFont(size=9),
            text_color="#444444",
        ).grid(row=5, column=0, pady=(0, 10), sticky="s")


class PageConnexion(ctk.CTkFrame):
    """
    Page intermediaire de connexion : saisie mot de passe + Gold Code 2FA.
    Logo en fond semi-transparent.
    """

    def __init__(self, master, callback_valider, callback_retour, **kwargs):
        super().__init__(master, fg_color=COULEUR_FOND, **kwargs)
        self.callback_valider = callback_valider
        self.callback_retour = callback_retour
        self._construire()

    def _construire(self):
        """Construit les widgets de la page de connexion."""
        self.grid_rowconfigure(list(range(10)), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Logo fond ---
        chemin_logo = os.path.join("assets", "logo.png")
        if os.path.exists(chemin_logo):
            try:
                img_brute = Image.open(chemin_logo).convert("RGBA")
                img_brute.putalpha(
                    img_brute.getchannel("A").point(lambda p: int(p * 0.12))
                )
                img_ctk = ctk.CTkImage(
                    light_image=img_brute,
                    dark_image=img_brute,
                    size=(300, 300),
                )
                lbl_logo = ctk.CTkLabel(self, image=img_ctk, text="")
                lbl_logo.grid(row=0, column=0, rowspan=10, sticky="nsew")
                lbl_logo.lower()
            except Exception:
                pass

        # --- Titre ---
        ctk.CTkLabel(
            self,
            text="AUTHENTIFICATION",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COULEUR_OR,
        ).grid(row=0, column=0, pady=(50, 5), sticky="s")

        ctk.CTkLabel(
            self,
            text=f"Habilitation niveau {HABILITATION_MIN} requise",
            font=ctk.CTkFont(size=12),
            text_color=COULEUR_DANGER,
        ).grid(row=1, column=0, pady=(0, 30))

        # --- Cadre central ---
        cadre = ctk.CTkFrame(self, fg_color=COULEUR_ACCENT, corner_radius=12, width=420)
        cadre.grid(row=2, column=0, rowspan=5, padx=40, pady=10, sticky="n")
        cadre.grid_columnconfigure(0, weight=1)

        # Mot de passe
        ctk.CTkLabel(
            cadre,
            text="Mot de passe maitre :",
            font=ctk.CTkFont(size=13),
            text_color=COULEUR_TEXTE,
        ).grid(row=0, column=0, padx=30, pady=(25, 5), sticky="w")

        self.champ_mdp = ctk.CTkEntry(
            cadre,
            show="*",
            width=360,
            height=42,
            font=ctk.CTkFont(size=14),
            placeholder_text="Saisir le mot de passe...",
        )
        self.champ_mdp.grid(row=1, column=0, padx=30, pady=(0, 15))

        # Gold Code 2FA
        ctk.CTkLabel(
            cadre,
            text="Gold Code (Google Authenticator) :",
            font=ctk.CTkFont(size=13),
            text_color=COULEUR_TEXTE,
        ).grid(row=2, column=0, padx=30, pady=(0, 5), sticky="w")

        self.champ_code = ctk.CTkEntry(
            cadre,
            width=360,
            height=42,
            font=ctk.CTkFont(size=14),
            placeholder_text="Code a 6 chiffres...",
        )
        self.champ_code.grid(row=3, column=0, padx=30, pady=(0, 10))

        # Message d'erreur
        self.lbl_erreur = ctk.CTkLabel(
            cadre,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COULEUR_DANGER,
        )
        self.lbl_erreur.grid(row=4, column=0, padx=30, pady=(0, 10))

        # Bouton valider
        BoutonAnimé(
            cadre,
            text="VALIDER",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#0F3460",
            hover_color="#16213E",
            text_color=COULEUR_OR,
            width=360,
            height=48,
            corner_radius=8,
            command=self._valider,
        ).grid(row=5, column=0, padx=30, pady=(5, 25))

        # Bouton retour
        BoutonAnimé(
            self,
            text="Retour",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="#1A1A2E",
            text_color="#666666",
            width=100,
            height=32,
            command=self.callback_retour,
        ).grid(row=7, column=0, pady=10)

    def _valider(self):
        """Recupere les saisies et les passe au callback de validation."""
        mdp = self.champ_mdp.get()
        code = self.champ_code.get()
        if not mdp or not code:
            self.lbl_erreur.configure(text="Tous les champs sont obligatoires.")
            return
        self.lbl_erreur.configure(text="")
        self.callback_valider(mdp, code)

    def afficher_erreur(self, message: str):
        """Affiche un message d'erreur dans le formulaire."""
        self.lbl_erreur.configure(text=message)


class PageDashboard(ctk.CTkFrame):
    """
    Tableau de bord principal apres authentification reussie.
    Acces aux 8 modules operationnels.
    """

    MODULES = [
        ("Authentification", "modules.auth.auth"),
        ("Personne Recherchee", "modules.personne_recherchee.personne_recherchee"),
        ("Recherche Camera", "modules.recherche_camera.recherche_camera"),
        ("Reconnaissance Faciale", "modules.reconnaissance_faciale.reconnaissance_faciale"),
        ("Base de Donnees", "modules.base_donnees.base_donnees"),
        ("Recherche Web", "modules.recherche_web.recherche_web"),
        ("Surveillance", "modules.surveillance.surveillance"),
        ("Triangulation", "modules.triangulation.triangulation"),
    ]

    def __init__(self, master, callback_deconnexion, **kwargs):
        super().__init__(master, fg_color=COULEUR_FOND, **kwargs)
        self.callback_deconnexion = callback_deconnexion
        self._construire()

    def _construire(self):
        """Construit le tableau de bord avec les boutons modules."""
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- En-tete ---
        entete = ctk.CTkFrame(self, fg_color=COULEUR_ACCENT, height=70, corner_radius=0)
        entete.grid(row=0, column=0, sticky="ew")
        entete.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            entete,
            text=f"{APP_NOM.upper()}  v{APP_VERSION}  |  {APP_EDITEUR}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COULEUR_OR,
        ).grid(row=0, column=0, pady=20, sticky="w", padx=30)

        BoutonAnimé(
            entete,
            text="Deconnexion",
            font=ctk.CTkFont(size=12),
            fg_color=COULEUR_DANGER,
            hover_color="#AA2222",
            text_color="white",
            width=130,
            height=36,
            command=self.callback_deconnexion,
        ).grid(row=0, column=1, pady=17, padx=20, sticky="e")

        # --- Sous-titre ---
        ctk.CTkLabel(
            self,
            text="Selectionner un module operationnel",
            font=ctk.CTkFont(size=14),
            text_color="#888888",
        ).grid(row=1, column=0, pady=(20, 10))

        # --- Grille des modules ---
        grille = ctk.CTkFrame(self, fg_color="transparent")
        grille.grid(row=2, column=0, padx=40, pady=20, sticky="nsew")

        for i in range(4):
            grille.grid_columnconfigure(i, weight=1)
        for j in range(2):
            grille.grid_rowconfigure(j, weight=1)

        for idx, (nom, _module) in enumerate(self.MODULES):
            ligne = idx // 4
            col = idx % 4
            BoutonAnimé(
                grille,
                text=nom.upper(),
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=COULEUR_ACCENT,
                hover_color="#16213E",
                text_color=COULEUR_OR,
                height=90,
                corner_radius=10,
                command=lambda m=nom: self._ouvrir_module(m),
            ).grid(row=ligne, column=col, padx=10, pady=10, sticky="nsew")

    def _ouvrir_module(self, nom_module: str):
        """Ouvre la fenetre du module selectionne (TODO : brancher chaque module)."""
        # TODO : instancier et afficher la fenetre du module correspondant
        print(f"[DASHBOARD] Ouverture du module : {nom_module}")


class MainWindow:
    """
    Controleur principal de l'application Oeil de Dieu.
    Gere la navigation entre les pages : Accueil -> Connexion -> Dashboard.
    S'ouvre en plein ecran par defaut (Windows et Linux).
    """

    def __init__(self):
        self.window = ctk.CTk()
        self.window.title(f"{APP_NOM} v{APP_VERSION} - {APP_EDITEUR}")
        self.window.configure(fg_color=COULEUR_FOND)

        # --- Plein ecran selon le systeme d'exploitation ---
        os_courant = platform.system()
        if os_courant == "Windows":
            self.window.state("zoomed")
        elif os_courant == "Linux":
            self.window.attributes("-zoomed", True)
        else:
            # MacOS ou autre : maximiser manuellement
            largeur = self.window.winfo_screenwidth()
            hauteur = self.window.winfo_screenheight()
            self.window.geometry(f"{largeur}x{hauteur}+0+0")

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self._page_courante = None
        self._afficher_accueil()

    def _vider_fenetre(self):
        """Detruit la page courante avant d'en charger une nouvelle."""
        if self._page_courante is not None:
            self._page_courante.destroy()
            self._page_courante = None

    def _afficher_accueil(self):
        """Affiche la page d'accueil."""
        self._vider_fenetre()
        self._page_courante = PageAccueil(
            self.window,
            callback_connexion=self._afficher_connexion,
        )
        self._page_courante.grid(row=0, column=0, sticky="nsew")

    def _afficher_connexion(self):
        """Affiche la page de connexion."""
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
        Redirige vers le dashboard si l'authentification reussit.
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
            # Fallback si le module auth n'est pas encore operationnel
            if isinstance(self._page_courante, PageConnexion):
                self._page_courante.afficher_erreur(
                    "[DEV] Module auth non disponible. Acces temporairement bloque."
                )

    def _afficher_dashboard(self):
        """Affiche le tableau de bord apres authentification reussie."""
        self._vider_fenetre()
        self._page_courante = PageDashboard(
            self.window,
            callback_deconnexion=self._afficher_accueil,
        )
        self._page_courante.grid(row=0, column=0, sticky="nsew")

    def run(self):
        """Lance la boucle principale de l'interface."""
        self.window.mainloop()
