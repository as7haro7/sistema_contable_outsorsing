import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app, g,Flask
import logging

class DatabaseManager:
    def __init__(self):
        self.master_connection = None
        self.company_connections = {}
    
    def get_master_connection(self):
        """Conexión a la base de datos maestra"""
        try:
            if self.master_connection is None or self.master_connection.closed:
                self.master_connection = psycopg2.connect(
                    host=current_app.config['MASTER_DB_HOST'],
                    port=current_app.config['MASTER_DB_PORT'],
                    database=current_app.config['MASTER_DB_NAME'],
                    user=current_app.config['MASTER_DB_USER'],
                    password=current_app.config['MASTER_DB_PASSWORD'],
                    cursor_factory=RealDictCursor
                )
            return self.master_connection
        except Exception as e:
            logging.error(f"Error conectando a BD maestra: {e}")
            raise
    
    def get_company_connection(self, empresa_id):
        """Conexión a base de datos de empresa específica"""
        # Corregido: Usar el formato correcto para el nombre de la base de datos
        db_name = f"{current_app.config['COMPANY_DB_PREFIX']}{empresa_id}"
        
        try:
            if empresa_id not in self.company_connections or self.company_connections[empresa_id].closed:
                self.company_connections[empresa_id] = psycopg2.connect(
                    host=current_app.config['MASTER_DB_HOST'],
                    port=current_app.config['MASTER_DB_PORT'],
                    database=db_name,
                    user=current_app.config['MASTER_DB_USER'],
                    password=current_app.config['MASTER_DB_PASSWORD'],
                    cursor_factory=RealDictCursor
                )
            return self.company_connections[empresa_id]
        except Exception as e:
            logging.error(f"Error conectando a BD empresa {empresa_id}: {e}")
            raise
    
    def execute_query(self, connection, query, params=None, fetch=True):
        """Ejecutar consulta SQL"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = None
                if fetch:
                    try:
                        result = cursor.fetchall()
                    except Exception:
                        result = None
                # Hacer commit SIEMPRE para operaciones de escritura
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                    connection.commit()
                return result if fetch else cursor.rowcount
        except Exception as e:
            connection.rollback()
            logging.error(f"Error ejecutando consulta: {e}")
            raise

# Instancia global
db_manager = DatabaseManager()




