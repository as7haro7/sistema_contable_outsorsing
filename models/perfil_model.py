from models.database import db_manager

class PerfilModel:
    @staticmethod
    def listar():
        conn = db_manager.get_master_connection()
        query = "SELECT id, nombre FROM perfiles WHERE activo = TRUE ORDER BY nombre"
        return db_manager.execute_query(conn, query)