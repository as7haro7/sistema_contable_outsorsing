from models.database import db_manager

class GestionModel:
    @staticmethod
    def listar_gestiones(empresa_id):
        conn = db_manager.get_master_connection()
        query = """
            SELECT id, descripcion, periodo, fecha_inicio, fecha_fin, activo, cerrada
            FROM gestiones
            WHERE empresa_id = %(empresa_id)s
            ORDER BY periodo DESC
        """
        return db_manager.execute_query(conn, query, {'empresa_id': empresa_id})

    @staticmethod
    def crear_gestion(data):
        conn = db_manager.get_master_connection()
        query = """
            INSERT INTO gestiones (empresa_id, descripcion, periodo, fecha_inicio, fecha_fin, codigo_moneda, nombre_moneda, usuario_creacion)
            VALUES (%(empresa_id)s, %(descripcion)s, %(periodo)s, %(fecha_inicio)s, %(fecha_fin)s, %(codigo_moneda)s, %(nombre_moneda)s, %(usuario_creacion)s)
            RETURNING id
        """
        return db_manager.execute_query(conn, query, data)

    @staticmethod
    def obtener_gestion(id):
        conn = db_manager.get_master_connection()
        query = "SELECT * FROM gestiones WHERE id = %(id)s"
        result = db_manager.execute_query(conn, query, {'id': id})
        return result[0] if result else None

    @staticmethod
    def actualizar_gestion(id, data):
        conn = db_manager.get_master_connection()
        query = """
            UPDATE gestiones
            SET descripcion = %(descripcion)s, periodo = %(periodo)s, fecha_inicio = %(fecha_inicio)s, fecha_fin = %(fecha_fin)s, codigo_moneda = %(codigo_moneda)s, nombre_moneda = %(nombre_moneda)s, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING id
        """
        data['id'] = id
        return db_manager.execute_query(conn, query, data)

    @staticmethod
    def eliminar_gestion(id):
        conn = db_manager.get_master_connection()
        query = "DELETE FROM gestiones WHERE id = %(id)s RETURNING id"
        return db_manager.execute_query(conn, query, {'id': id})