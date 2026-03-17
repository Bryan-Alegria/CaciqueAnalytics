"""
Database Connection Utility - PostgreSQL
Gestiona conexión a cacique_analytics
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
import logging

logger = logging.getLogger("db_connection")

class DatabaseConnection:
    """
    Wrapper para conexión PostgreSQL con pool y manejo de errores
    """

    def __init__(self):
        """
        Inicializa conexión desde variables de entorno
        """
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "cacique_analytics")
        self.user = os.getenv("DB_USER", "cacique_app")
        self.password = os.getenv("DB_PASSWORD")

        if not self.password:
            raise ValueError("DB_PASSWORD no configurada en .env")

        self.connection: Optional[psycopg2.extensions.connection] = None

    def connect(self):
        """
        Establece conexión con PostgreSQL
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Conexión exitosa a {self.database}")
        except psycopg2.Error as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            raise

    def disconnect(self):
        """
        Cierra conexión
        """
        if self.connection:
            self.connection.close()
            logger.info("Conexión cerrada")

    def execute_query(self, query: str, params: tuple = None):
        """
        Ejecuta query SELECT y retorna resultados

        Args:
            query: SQL query
            params: Parámetros para query parametrizada

        Returns:
            Lista de diccionarios con resultados
        """
        if not self.connection:
            self.connect()

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_insert(self, query: str, params: tuple):
        """
        Ejecuta INSERT y hace commit

        Args:
            query: SQL INSERT
            params: Valores a insertar

        Returns:
            ID del registro insertado (si RETURNING id)
        """
        if not self.connection:
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                if cursor.description:
                    return cursor.fetchone()
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Error en INSERT: {e}")
            raise
