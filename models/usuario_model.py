from models.database import db_manager
from werkzeug.security import generate_password_hash, check_password_hash

class UsuarioModel:
    @staticmethod
    def listar():
        conn = db_manager.get_master_connection()
        query = """
            SELECT u.id, u.username, u.nombre_completo, u.email, u.activo, u.es_super_usuario,
                   string_agg(e.razon_social, ', ') as empresas
            FROM usuarios u
            LEFT JOIN usuario_empresas ue ON u.id = ue.usuario_id
            LEFT JOIN empresas e ON ue.empresa_id = e.id
            WHERE u.activo = TRUE
            GROUP BY u.id, u.username, u.nombre_completo, u.email, u.activo, u.es_super_usuario
            ORDER BY u.nombre_completo
        """
        return db_manager.execute_query(conn, query)

    @staticmethod
    def obtener(id):
        conn = db_manager.get_master_connection()
        query = "SELECT * FROM usuarios WHERE id = %s"
        result = db_manager.execute_query(conn, query, (id,))
        return result[0] if result else None

    @staticmethod
    def obtener_por_username(username):
        conn = db_manager.get_master_connection()
        query = "SELECT * FROM usuarios WHERE username = %s"
        result = db_manager.execute_query(conn, query, (username,))
        return result[0] if result else None

    @staticmethod
    def crear(data):
        conn = db_manager.get_master_connection()
        query = """
            INSERT INTO usuarios (username, email, nombre_completo, password_hash, salt, es_super_usuario, activo)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            RETURNING id
        """
        params = (
            data['username'],
            data['email'],
            data['nombre_completo'],
            data['password'],  # Contraseña en texto plano
            '',                # salt vacío
            data.get('es_super_usuario', False)
        )
        result = db_manager.execute_query(conn, query, params)
        user_id = result[0]['id'] if result else None

        # Asignar empresas si corresponde
        if user_id and data.get('empresas'):
            for empresa_id in data['empresas']:
                db_manager.execute_query(
                    conn,
                    "INSERT INTO usuario_empresas (usuario_id, empresa_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (user_id, empresa_id),
                    fetch=False
                )
        return user_id

    @staticmethod
    def actualizar(id, data):
        conn = db_manager.get_master_connection()
        set_clauses = []
        params = []
        if 'nombre_completo' in data:
            set_clauses.append("nombre_completo = %s")
            params.append(data['nombre_completo'])
        if 'email' in data:
            set_clauses.append("email = %s")
            params.append(data['email'])
        if 'es_super_usuario' in data:
            set_clauses.append("es_super_usuario = %s")
            params.append(data['es_super_usuario'])
        if 'activo' in data:
            set_clauses.append("activo = %s")
            params.append(data['activo'])
        if 'password' in data and data['password']:
            salt = "s4lt"
            password_hash = generate_password_hash(data['password'] + salt)
            set_clauses.append("password_hash = %s")
            set_clauses.append("salt = %s")
            params.append(password_hash)
            params.append(salt)
        if not set_clauses:
            return False
        query = f"UPDATE usuarios SET {', '.join(set_clauses)} WHERE id = %s"
        params.append(id)
        db_manager.execute_query(conn, query, tuple(params), fetch=False)

        # Actualizar empresas asignadas
        if 'empresas' in data:
            db_manager.execute_query(conn, "DELETE FROM usuario_empresas WHERE usuario_id = %s", (id,), fetch=False)
            for empresa_id in data['empresas']:
                db_manager.execute_query(
                    conn,
                    "INSERT INTO usuario_empresas (usuario_id, empresa_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (id, empresa_id),
                    fetch=False
                )
        return True

    # @staticmethod
    # def eliminar(id):
    #     conn = db_manager.get_master_connection()
    #     db_manager.execute_query(conn, "UPDATE usuarios SET activo = FALSE WHERE id = %s", (id,), fetch=False)
    #     return True
    
    @staticmethod
    def eliminar(id):
        conn = db_manager.get_master_connection()
        db_manager.execute_query(conn, "DELETE FROM usuarios WHERE id = %s", (id,), fetch=False)
        return True

    @staticmethod
    def empresas_disponibles():
        conn = db_manager.get_master_connection()
        query = "SELECT id, razon_social FROM empresas WHERE activo = TRUE ORDER BY razon_social"
        return db_manager.execute_query(conn, query)
    
    @staticmethod
    def get_user_companies(username):
        """
        Devuelve las empresas asignadas a un usuario por su username.
        """
        conn = db_manager.get_master_connection()
        query = """
            SELECT e.id, e.razon_social
            FROM empresas e
            INNER JOIN usuario_empresas ue ON e.id = ue.empresa_id
            INNER JOIN usuarios u ON ue.usuario_id = u.id
            WHERE u.username = %s AND ue.activo = TRUE
        """
        return db_manager.execute_query(conn, query, (username,))

    @staticmethod
    def asignar_permisos_usuario(usuario_id, data, asignado_por):
        conn = db_manager.get_master_connection()
        query = """
            INSERT INTO permisos_usuario (
                usuario_id, perfil_id, puede_crear, puede_actualizar, puede_eliminar, puede_imprimir, puede_exportar, asignado_por
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            usuario_id,
            data['perfil_id'],
            bool(data.get('puede_crear')),
            bool(data.get('puede_actualizar')),
            bool(data.get('puede_eliminar')),
            bool(data.get('puede_imprimir')),
            bool(data.get('puede_exportar')),
            asignado_por
        )
        db_manager.execute_query(conn, query, params, fetch=False)

    @staticmethod
    def actualizar_permisos_usuario(usuario_id, data, asignado_por):
        conn = db_manager.get_master_connection()
        # Elimina los permisos anteriores (si solo debe haber uno por usuario)
        db_manager.execute_query(conn, "DELETE FROM permisos_usuario WHERE usuario_id = %s", (usuario_id,), fetch=False)
        # Inserta los nuevos permisos
        query = """
            INSERT INTO permisos_usuario (
                usuario_id, perfil_id, puede_crear, puede_actualizar, puede_eliminar, puede_imprimir, puede_exportar, asignado_por
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            usuario_id,
            data['perfil_id'],
            bool(data.get('puede_crear')),
            bool(data.get('puede_actualizar')),
            bool(data.get('puede_eliminar')),
            bool(data.get('puede_imprimir')),
            bool(data.get('puede_exportar')),
            asignado_por
        )
        db_manager.execute_query(conn, query, params, fetch=False)

    @staticmethod
    def get_permisos_usuario(usuario_id):
        conn = db_manager.get_master_connection()
        query = """
            SELECT puede_crear, puede_actualizar, puede_eliminar, puede_imprimir, puede_exportar
            FROM permisos_usuario
            WHERE usuario_id = %s
            LIMIT 1
        """
        result = db_manager.execute_query(conn, query, (usuario_id,))
        if result:
            return result[0]
        # Si no hay permisos, retorna todos en False para evitar errores en el template
        return {
            'puede_crear': False,
            'puede_actualizar': False,
            'puede_eliminar': False,
            'puede_imprimir': False,
            'puede_exportar': False
        }
    
    @staticmethod
    def get_perfil_id_usuario(usuario_id):
        """
        Devuelve el perfil_id actual del usuario desde la tabla permisos_usuario.
        """
        conn = db_manager.get_master_connection()
        query = """
            SELECT perfil_id
            FROM permisos_usuario
            WHERE usuario_id = %s
            ORDER BY fecha_asignacion DESC LIMIT 1
        """
        result = db_manager.execute_query(conn, query, (usuario_id,))
        if result:
            return result[0]['perfil_id']
        return None