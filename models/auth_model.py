from models.database import db_manager
from werkzeug.security import check_password_hash
from datetime import datetime

class AuthModel:
    @staticmethod
    def authenticate_user(username, password):
        """Autenticar usuario"""
        connection = db_manager.get_master_connection()
        
        query = """
            SELECT u.username, u.nombre_completo, u.password_hash, ue.empresa_id, e.razon_social as empresa_nombre
            FROM usuarios u
            INNER JOIN usuario_empresas ue ON u.id = ue.usuario_id
            INNER JOIN empresas e ON ue.empresa_id = e.id
            WHERE u.username = %s
            LIMIT 1
        """
        
        result = db_manager.execute_query(connection, query, (username,))
        
        if result and len(result) > 0:
            user = result[0]
            # Sin hash - comparación directa (NO RECOMENDADO EN PRODUCCIÓN)
            if user['password_hash'] == password:  # O usa check_password_hash si corresponde
                return {
                    'usuario': user['username'],
                    'nombre': user['nombre_completo'],
                    'id_empresa': user['empresa_id'],
                    'empresa_nombre': user['empresa_nombre']
                }
        
        return None
    
    @staticmethod
    def get_user_permissions(username):
        """Obtener permisos del usuario"""
        connection = db_manager.get_master_connection()
        query = """
            SELECT p.codigo as perfil, 
                   pu.puede_crear, pu.puede_leer, pu.puede_actualizar, pu.puede_eliminar, pu.puede_imprimir, pu.puede_exportar,
                   p.nombre as perfil_nombre, p.ruta
            FROM usuarios u
            INNER JOIN permisos_usuario pu ON u.id = pu.usuario_id
            INNER JOIN perfiles p ON pu.perfil_id = p.id
            WHERE u.username = %s AND pu.activo = TRUE AND p.activo = TRUE
        """
        return db_manager.execute_query(connection, query, (username,))
    
    @staticmethod
    def get_user_companies(username):
        """Obtener empresas accesibles por el usuario"""
        connection = db_manager.get_master_connection()
        
        query = """
            SELECT e.id, e.razon_social AS razon, e.nit
            FROM empresas e
            INNER JOIN usuario_empresas ue ON e.id = ue.empresa_id
            INNER JOIN usuarios u ON ue.usuario_id = u.id
            WHERE u.username = %s
        """
        
        return db_manager.execute_query(connection, query, (username,))
    @staticmethod
    def get_company_gestiones(empresa_id):
        """Obtener gestiones de una empresa"""
        connection = db_manager.get_master_connection()
        
        query = """
            SELECT id, descripcion AS descrip, periodo AS gestion, fecha_inicio AS fecha_ini, fecha_fin, codigo_moneda AS moneda
            FROM gestiones
            WHERE empresa_id = %s
            ORDER BY fecha_inicio DESC
        """
        
        return db_manager.execute_query(connection, query, (empresa_id,))