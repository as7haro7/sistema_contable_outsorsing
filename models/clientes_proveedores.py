from flask import session
from models.database import db_manager

class TerceroModel:
    @staticmethod
    def get_all(tipo=None):
        """
        Listar todos los terceros (clientes y/o proveedores) de la empresa activa usando SP.
        tipo: 'cliente', 'proveedor' o None (ambos)
        """
        connection = db_manager.get_company_connection(session['empresa_id'])
        # El SP `sp_get_all_terceros` maneja la lógica de filtrar por tipo
        # y combina los resultados de clientes y proveedores.
        query = "SELECT * FROM sp_get_all_terceros(%s);"
        return db_manager.execute_query(connection, query, (tipo,))

    @staticmethod
    def get_by_id(tercero_id, tipo):
        """Obtener un tercero por ID y tipo ('cliente' o 'proveedor') usando SF."""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = "SELECT * FROM sf_get_cliente_by_id(%s);"
        elif tipo == 'proveedor':
            query = "SELECT * FROM sf_get_proveedor_by_id(%s);"
        else:
            return None
        result = db_manager.execute_query(connection, query, (tercero_id,))
        return result[0] if result else None

    @staticmethod
    def create(data, tipo):
        """Crear un nuevo tercero (cliente o proveedor) usando SP."""
        connection = db_manager.get_company_connection(session['empresa_id'])
        usuario = session.get('user_nombre', 'sistema')
        if tipo == 'cliente':
            query = "SELECT id FROM sp_create_cliente(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            params = (
                data['razon'], data['nit'], data.get('telf', ''), data.get('celular', ''),
                data.get('email', ''), data.get('pais', ''), data.get('depto', ''),
                data.get('domicilio', ''), usuario
            )
        elif tipo == 'proveedor':
            query = "SELECT id FROM sp_create_proveedor(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            params = (
                data['razon'], data['nit'], data.get('autorizacion', ''), data.get('telf', ''),
                data.get('celular', ''), data.get('email', ''), data.get('pais', ''),
                data.get('depto', ''), data.get('domicilio', ''), usuario
            )
        else:
            return None
        result = db_manager.execute_query(connection, query, params)
        return result[0]['id'] if result else None

    @staticmethod
    def update(tercero_id, data, tipo):
        """Actualizar un tercero (cliente o proveedor) usando SP."""
        connection = db_manager.get_company_connection(session['empresa_id'])
        usuario = session.get('user_nombre', 'sistema')
        if tipo == 'cliente':
            query = "SELECT 1 FROM sp_update_cliente(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            params = (
                tercero_id, data['razon'], data['nit'], data.get('telf', ''), data.get('celular', ''),
                data.get('email', ''), data.get('pais', ''), data.get('depto', ''),
                data.get('domicilio', ''), usuario
            )
        elif tipo == 'proveedor':
            query = "SELECT 1 FROM sp_update_proveedor(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            params = (
                tercero_id, data['razon'], data['nit'], data.get('autorizacion', ''), data.get('telf', ''),
                data.get('celular', ''), data.get('email', ''), data.get('pais', ''),
                data.get('depto', ''), data.get('domicilio', ''), usuario
            )
        else:
            return None
        return db_manager.execute_query(connection, query, params, fetch=False)

    @staticmethod
    def delete(tercero_id, tipo):
        """Eliminar (lógico, si se implementa en SP) un tercero (cliente o proveedor) usando SP."""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = "SELECT 1 FROM sp_delete_cliente(%s);"
        elif tipo == 'proveedor':
            query = "SELECT 1 FROM sp_delete_proveedor(%s);"
        else:
            return None
        return db_manager.execute_query(connection, query, (tercero_id,), fetch=False)

    @staticmethod
    def get_contactos(tercero_id, tipo):
        """Obtener contactos asociados a un tercero usando SF."""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = "SELECT * FROM sf_get_cliente_contactos(%s);"
        elif tipo == 'proveedor':
            query = "SELECT * FROM sf_get_proveedor_contactos(%s);"
        else:
            return []
        return db_manager.execute_query(connection, query, (tercero_id,))

    @staticmethod
    def add_contacto(tercero_id, data, tipo):
        """Agregar contacto a un tercero usando SP."""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = "SELECT 1 FROM sp_add_cliente_contacto(%s, %s, %s, %s, %s);"
            params = (tercero_id, data['nombre'], data.get('telf', ''), data.get('celular', ''), data.get('email', ''))
        elif tipo == 'proveedor':
            query = "SELECT 1 FROM sp_add_proveedor_contacto(%s, %s, %s, %s, %s);"
            params = (tercero_id, data['nombre'], data.get('telf', ''), data.get('celular', ''), data.get('email', ''))
        else:
            return None
        return db_manager.execute_query(connection, query, params, fetch=False)