#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Module : Recherche Web
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Effectuer des recherches web sur une cible (nom, alias, numero)
    - Parser les resultats HTML via BeautifulSoup
    - Retourner des resultats structures (titre, url, extrait)
  AVERTISSEMENT : Utiliser uniquement dans un cadre legal autorise.
=============================================================================
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ResultatRecherche:
    """Un resultat de recherche web."""
    titre: str
    url: str
    extrait: str
    source: str = "web"


class RechercheWeb:
    """
    Moteur de recherche web pour Oeil de Dieu.
    Interroge les moteurs publics et parse les resultats.
    """

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    TIMEOUT = 10  # secondes

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(self.HEADERS)

    def rechercher(self, requete: str, max_resultats: int = 10) -> List[ResultatRecherche]:
        """
        Effectue une recherche web pour la requete donnee.
        Retourne jusqu'a max_resultats resultats structures.

        TODO : integrer une API de recherche (SerpAPI, DuckDuckGo API)
               pour des resultats plus fiables et conformes aux CGU.
        """
        # TODO : remplacer le scraping par une API de recherche dediee
        resultats: List[ResultatRecherche] = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(requete)}"
            reponse = self._session.get(url, timeout=self.TIMEOUT)
            reponse.raise_for_status()
            soup = BeautifulSoup(reponse.text, "html.parser")

            for bloc in soup.select(".result")[:max_resultats]:
                lien_tag = bloc.select_one(".result__a")
                extrait_tag = bloc.select_one(".result__snippet")

                if not lien_tag:
                    continue

                titre = lien_tag.get_text(strip=True)
                href = lien_tag.get("href", "")
                extrait = extrait_tag.get_text(strip=True) if extrait_tag else ""

                resultats.append(ResultatRecherche(
                    titre=titre,
                    url=href,
                    extrait=extrait,
                ))
        except requests.RequestException:
            pass  # Echec reseau : retourner liste vide sans planter

        return resultats

    def rechercher_personne(
        self,
        nom: str,
        prenom: str = "",
        alias: str = "",
        max_resultats: int = 10,
    ) -> List[ResultatRecherche]:
        """
        Recherche une personne par nom, prenom et/ou alias.
        Construit automatiquement la requete optimale.
        """
        termes = " ".join(t for t in [prenom, nom, alias] if t)
        if not termes:
            return []
        return self.rechercher(termes, max_resultats)

    def obtenir_page(self, url: str) -> Optional[str]:
        """
        Recupere le contenu texte brut d'une page web.
        Retourne None en cas d'echec.
        """
        try:
            reponse = self._session.get(url, timeout=self.TIMEOUT)
            reponse.raise_for_status()
            soup = BeautifulSoup(reponse.text, "html.parser")
            return soup.get_text(separator=" ", strip=True)
        except requests.RequestException:
            return None

    def __del__(self):
        """Ferme la session HTTP a la destruction."""
        self._session.close()
