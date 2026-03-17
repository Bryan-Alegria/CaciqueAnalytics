"""
Base Extractor - Clase abstracta para todos los extractores
Define interfaz común para FBref, SofaScore, FotMob, Transfermarkt
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging

class BaseExtractor(ABC):
    """
    Extractor base con métodos comunes de reintento y logging
    """

    def __init__(self, source_name: str):
        """
        Inicializa extractor con configuración básica

        Args:
            source_name: Nombre de la fuente (sofascore, fbref, fotmob, transfermarkt)
        """
        self.source_name = source_name
        self.logger = logging.getLogger(f"extractor.{source_name}")

    @abstractmethod
    def extract_season_matches(self, league_id: int, season_id: int) -> List[Dict]:
        """
        Extrae partidos de una temporada

        Args:
            league_id: ID de la liga en la fuente
            season_id: ID de la temporada en la fuente

        Returns:
            Lista de diccionarios con datos de partidos
        """
        pass

    @abstractmethod
    def extract_player_stats(self, player_id: int, season_id: int) -> Optional[Dict]:
        """
        Extrae estadísticas de un jugador en una temporada

        Args:
            player_id: ID del jugador en la fuente
            season_id: ID de la temporada

        Returns:
            Diccionario con estadísticas o None si no existe
        """
        pass

    def log_extraction(self, entity: str, count: int):
        """
        Registra extracción completada

        Args:
            entity: Tipo de entidad extraída (matches, players, stats)
            count: Cantidad de registros extraídos
        """
        self.logger.info(f"Extraídos {count} {entity} desde {self.source_name}")
