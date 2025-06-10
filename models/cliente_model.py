from flask import session
from models.database import db_manager

class ClienteModel:
    @staticmethod
    def get_all():
        """Obtener todos los clientes"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT c.*, t.nombre as tipo_nombre
            FROM clientes c
            LEFT JOIN tipos_cliente t ON c.tipo_cliente = t.id
            WHERE c.estado = 'ACTIVO'
            ORDER BY c.nombre
        """
        
        return db_manager.execute_query(connection, query)
    
    @staticmethod
    def get_by_id(cliente_id):
        """Obtener cliente por ID"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT c.*, t.nombre as tipo_nombre
            FROM clientes c
            LEFT JOIN tipos_cliente t ON c.tipo_cliente = t.id
            WHERE c.id = %s
        """
        
        result = db_manager.execute_query(connection, query, (cliente_id,))
        return result[0] if result else None
    
    @staticmethod
    def create(data):
        """Crear nuevo cliente"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            INSERT INTO clientes (nombre, nit, direccion, telefono, email, tipo_cliente, estado, usuario, fechasys)
            VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVO', %s, NOW())
            RETURNING id
        """
        
        params = (
            data['nombre'], data['nit'], data.get('direccion', ''),
            data.get('telefono', ''), data.get('email', ''),
            data.get('tipo_cliente', 1), session['user_id']
        )
        
        result = db_manager.execute_query(connection, query, params)
        return result[0]['id'] if result else None
    
    @staticmethod
    def update(cliente_id, data):
        """Actualizar cliente"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            UPDATE clientes
            SET nombre = %s, nit = %s, direccion = %s, telefono = %s, email = %s, tipo_cliente = %s
            WHERE id = %s
        """
        
        params = (
            data['nombre'], data['nit'], data.get('direccion', ''),
            data.get('telefono', ''), data.get('email', ''),
            data.get('tipo_cliente', 1), cliente_id
        )
        
        return db_manager.execute_query(connection, query, params, fetch=False)
    
    @staticmethod
    def delete(cliente_id):
        """Eliminar cliente (cambiar estado a INACTIVO)"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            UPDATE clientes SET estado = 'INACTIVO' WHERE id = %s
        """
        
        return db_manager.execute_query(connection, query, (cliente_id,), fetch=False)
    
    @staticmethod
    def get_tipos_cliente():
        """Obtener tipos de cliente"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = "SELECT * FROM tipos_cliente ORDER BY nombre"
        return db_manager.execute_query(connection, query)