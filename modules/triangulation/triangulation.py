#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  OEIL DE DIEU v1.0 - Module : Triangulation
  NAG NAT Industries - 2026
=============================================================================
  Responsabilites :
    - Calculer la position estimee d'une cible a partir de plusieurs
      points de detection (cameras, signalements)
    - Generer des cartes de chaleur de presence via Folium
    - Calculer les distances et caps entre points GPS
  Stack : geopy, folium, networkx
=============================================================================
"""

import folium
from geopy.distance import geodesic
from geopy.point import Point
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PointDetection:
    """Un point de detection : coordonnees GPS + horodatage + source."""
    latitude: float
    longitude: float
    horodatage: str        # ISO 8601
    source: str = ""      # Identifiant de la camera ou du capteur
    confiance: float = 1.0  # 0.0 - 1.0


class Triangulation:
    """
    Moteur de triangulation geographique pour Oeil de Dieu.
    Calcule la position estimee d'une cible et genere des cartes.
    """

    def __init__(self):
        self._points: List[PointDetection] = []

    def ajouter_point(self, point: PointDetection) -> None:
        """Ajoute un point de detection a l'historique."""
        self._points.append(point)

    def vider(self) -> None:
        """Supprime tous les points de detection."""
        self._points.clear()

    def centre_gravite(self) -> Optional[Tuple[float, float]]:
        """
        Calcule le barycentre pondere par la confiance de tous les points.
        Retourne (latitude, longitude) ou None si aucun point.
        """
        if not self._points:
            return None

        poids_total = sum(p.confiance for p in self._points)
        if poids_total == 0:
            return None

        lat_pond = sum(p.latitude * p.confiance for p in self._points) / poids_total
        lon_pond = sum(p.longitude * p.confiance for p in self._points) / poids_total
        return lat_pond, lon_pond

    def dernier_point(self) -> Optional[PointDetection]:
        """Retourne le point de detection le plus recent."""
        return self._points[-1] if self._points else None

    def distance_entre(
        self,
        point_a: Tuple[float, float],
        point_b: Tuple[float, float],
    ) -> float:
        """
        Calcule la distance geodesique en metres entre deux points GPS.
        Chaque point est un tuple (latitude, longitude).
        """
        return geodesic(point_a, point_b).meters

    def generer_carte(
        self,
        chemin_sortie: str = "carte_triangulation.html",
        zoom: int = 15,
    ) -> str:
        """
        Genere une carte Folium avec tous les points de detection.
        - Points de detection en rouge
        - Centre de gravite en jaune
        Retourne le chemin du fichier HTML genere.
        """
        centre = self.centre_gravite()
        if centre is None and self._points:
            centre = (self._points[0].latitude, self._points[0].longitude)
        elif centre is None:
            centre = (12.3647, -1.5337)  # Koudougou, Burkina Faso (defaut)

        carte = folium.Map(location=list(centre), zoom_start=zoom, tiles="CartoDB dark_matter")

        # Points de detection
        for pt in self._points:
            popup = (
                f"Source: {pt.source}<br>"
                f"Horodatage: {pt.horodatage}<br>"
                f"Confiance: {pt.confiance:.0%}"
            )
            folium.CircleMarker(
                location=[pt.latitude, pt.longitude],
                radius=8,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.7,
                popup=folium.Popup(popup, max_width=200),
            ).add_to(carte)

        # Centre de gravite
        if centre and self._points:
            folium.Marker(
                location=list(centre),
                icon=folium.Icon(color="orange", icon="crosshairs", prefix="fa"),
                popup="Position estimee (centre de gravite)",
            ).add_to(carte)

        # Trajets entre points consecutifs
        if len(self._points) >= 2:
            coords = [(p.latitude, p.longitude) for p in self._points]
            folium.PolyLine(
                coords, color="cyan", weight=2, opacity=0.6,
                tooltip="Trajectoire estimee",
            ).add_to(carte)

        carte.save(chemin_sortie)
        return chemin_sortie

    def rapport_positions(self) -> List[dict]:
        """Retourne tous les points sous forme de liste de dictionnaires."""
        return [
            {
                "latitude": p.latitude,
                "longitude": p.longitude,
                "horodatage": p.horodatage,
                "source": p.source,
                "confiance": p.confiance,
            }
            for p in self._points
        ]
