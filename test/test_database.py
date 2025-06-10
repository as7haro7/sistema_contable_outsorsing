# test_quick_db_manager.py
import os
from flask import Flask, g
import logging
import psycopg2 # Importar para capturar errores específicos
from models.database import DatabaseManager

# Configuración básica para la prueba (deberían coincidir con tu entorno)
class TestConfig:
    MASTER_DB_HOST = os.environ.get('MASTER_DB_HOST', 'localhost')
    MASTER_DB_PORT = int(os.environ.get('MASTER_DB_PORT', 5432))
    MASTER_DB_NAME = os.environ.get('MASTER_DB_NAME', 'test_master_db')
    MASTER_DB_USER = os.environ.get('MASTER_DB_USER', 'postgres')
    MASTER_DB_PASSWORD = os.environ.get('MASTER_DB_PASSWORD', 'mysecretpassword')
    COMPANY_DB_PREFIX = os.environ.get('COMPANY_DB_PREFIX', 'company_db_')

# Inicializa Flask para simular el contexto de la aplicación
app = Flask(__name__)
app.config.from_object(TestConfig)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Instancia global de tu DatabaseManager (si la tienes, si no, créala aquí)
db_manager = DatabaseManager()

def run_quick_test():
    with app.app_context():
        logging.info("Iniciando prueba rápida de DatabaseManager...")

        # --- Prueba de Conexión Maestra ---
        try:
            logging.info("Intentando obtener conexión a la BD Maestra...")
            master_conn = db_manager.get_master_connection()
            if master_conn and not master_conn.closed:
                logging.info("¡Conexión a BD Maestra exitosa!")
                
                # Ejecutar una consulta simple
                test_result = db_manager.execute_query(master_conn, "SELECT current_database() as db_name;")
                logging.info(f"Consulta en BD Maestra: {test_result}")
                assert test_result[0]['db_name'] == app.config['MASTER_DB_NAME']
                logging.info("Consulta en BD Maestra verificada.")
            else:
                logging.error("Fallo al obtener o validar la conexión a la BD Maestra.")
                return False
        except Exception as e:
            logging.error(f"Error crítico al conectar a la BD Maestra: {e}")
            return False

        # --- Prueba de Conexión a Base de Datos de Empresa ---
        empresa_id_test = 1 # Usa un ID de empresa que ya hayas creado o que sabes que puede crearse
        try:
            logging.info(f"Intentando obtener conexión a la BD de Empresa ID: {empresa_id_test}...")
            company_conn = db_manager.get_company_connection(empresa_id_test)
            if company_conn and not company_conn.closed:
                logging.info(f"¡Conexión a BD de Empresa {empresa_id_test} exitosa!")
                
                # Ejecutar una consulta simple
                test_result = db_manager.execute_query(company_conn, "SELECT current_database() as db_name;")
                expected_db_name = f"{app.config['COMPANY_DB_PREFIX']}{empresa_id_test}"
                logging.info(f"Consulta en BD de Empresa {empresa_id_test}: {test_result}")
                assert test_result[0]['db_name'] == expected_db_name
                logging.info(f"Consulta en BD de Empresa {empresa_id_test} verificada.")
            else:
                logging.error(f"Fallo al obtener o validar la conexión a la BD de Empresa {empresa_id_test}.")
                return False
        except Exception as e:
            logging.error(f"Error crítico al conectar a la BD de Empresa {empresa_id_test}: {e}")
            return False
            
        logging.info("¡Todas las pruebas rápidas superadas! Tu clase DatabaseManager parece funcionar.")
        return True

if __name__ == "__main__":
    if run_quick_test():
        print("\nRESULTADO: La clase DatabaseManager FUNCIONA correctamente para conexiones básicas.")
    else:
        print("\nRESULTADO: La clase DatabaseManager TIENE PROBLEMAS. Revisa los logs de error.")