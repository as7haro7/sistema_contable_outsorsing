from flask import session
from models.database import db_manager

class TerceroModel:
    @staticmethod
    def get_all(tipo=None):
        """
        Listar todos los terceros (clientes y/o proveedores) de la empresa activa.
        tipo: 'cliente', 'proveedor' o None (ambos)
        """
        connection = db_manager.get_company_connection(session['empresa_id'])
        terceros = []
        if tipo in (None, 'cliente'):
            query_cli = """
                SELECT 'cliente' as tipo, c.id, c.razon, c.nit, c.telf, c.celular, c.email, c.pais, c.depto, c.domicilio, c.usuario, c.fechasys
                FROM cliente c
                ORDER BY c.razon
            """
            terceros += db_manager.execute_query(connection, query_cli)
        if tipo in (None, 'proveedor'):
            query_prov = """
                SELECT 'proveedor' as tipo, p.id, p.razon, p.nit, p.telf, p.celular, p.email, p.pais, p.depto, p.domicilio, p.usuario, p.fechasys
                FROM proveedor p
                ORDER BY p.razon
            """
            terceros += db_manager.execute_query(connection, query_prov)
        return terceros

    @staticmethod
    def get_by_id(tercero_id, tipo):
        """Obtener un tercero por ID y tipo ('cliente' o 'proveedor')"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = "SELECT * FROM cliente WHERE id = %s"
        elif tipo == 'proveedor':
            query = "SELECT * FROM proveedor WHERE id = %s"
        else:
            return None
        result = db_manager.execute_query(connection, query, (tercero_id,))
        return result[0] if result else None

    @staticmethod
    def create(data, tipo):
        """Crear un nuevo tercero (cliente o proveedor)"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = """
                INSERT INTO cliente (razon, nit, telf, celular, email, pais, depto, domicilio, usuario, fechasys, horasys)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """
            params = (
                data['razon'], data['nit'], data.get('telf', ''), data.get('celular', ''),
                data.get('email', ''), data.get('pais', ''), data.get('depto', ''),
                data.get('domicilio', ''), session['usuario']
            )
        elif tipo == 'proveedor':
            query = """
                INSERT INTO proveedor (razon, nit, autorizacion, telf, celular, email, pais, depto, domicilio, usuario, fechasys, horasys)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """
            params = (
                data['razon'], data['nit'], data.get('autorizacion', ''), data.get('telf', ''),
                data.get('celular', ''), data.get('email', ''), data.get('pais', ''),
                data.get('depto', ''), data.get('domicilio', ''), session['usuario']
            )
        else:
            return None
        result = db_manager.execute_query(connection, query, params)
        return result[0]['id'] if result else None

    @staticmethod
    def update(tercero_id, data, tipo):
        """Actualizar un tercero (cliente o proveedor)"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = """
                UPDATE cliente
                SET razon=%s, nit=%s, telf=%s, celular=%s, email=%s, pais=%s, depto=%s, domicilio=%s, usuario=%s, fechasys=NOW(), horasys=NOW()
                WHERE id=%s
            """
            params = (
                data['razon'], data['nit'], data.get('telf', ''), data.get('celular', ''),
                data.get('email', ''), data.get('pais', ''), data.get('depto', ''),
                data.get('domicilio', ''), session['usuario'], tercero_id
            )
        elif tipo == 'proveedor':
            query = """
                UPDATE proveedor
                SET razon=%s, nit=%s, autorizacion=%s, telf=%s, celular=%s, email=%s, pais=%s, depto=%s, domicilio=%s, usuario=%s, fechasys=NOW(), horasys=NOW()
                WHERE id=%s
            """
            params = (
                data['razon'], data['nit'], data.get('autorizacion', ''), data.get('telf', ''),
                data.get('celular', ''), data.get('email', ''), data.get('pais', ''),
                data.get('depto', ''), data.get('domicilio', ''), session['usuario'], tercero_id
            )
        else:
            return None
        return db_manager.execute_query(connection, query, params, fetch=False)

    @staticmethod
    def delete(tercero_id, tipo):
        """Eliminar (lógico) un tercero (cliente o proveedor)"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = "DELETE FROM cliente WHERE id = %s"
        elif tipo == 'proveedor':
            query = "DELETE FROM proveedor WHERE id = %s"
        else:
            return None
        return db_manager.execute_query(connection, query, (tercero_id,), fetch=False)

    @staticmethod
    def get_contactos(tercero_id, tipo):
        """Obtener contactos asociados a un tercero"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = "SELECT * FROM Cliente_contacto WHERE id_cliente = %s"
        elif tipo == 'proveedor':
            query = "SELECT * FROM Proveedor_contacto WHERE id_proveedor = %s"
        else:
            return []
        return db_manager.execute_query(connection, query, (tercero_id,))

    @staticmethod
    def add_contacto(tercero_id, data, tipo):
        """Agregar contacto a un tercero"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        if tipo == 'cliente':
            query = """
                INSERT INTO Cliente_contacto (id_cliente, nombre, telf, celular, email)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (tercero_id, data['nombre'], data.get('telf', ''), data.get('celular', ''), data.get('email', ''))
        elif tipo == 'proveedor':
            query = """
                INSERT INTO Proveedor_contacto (id_proveedor, nombre, telf, celular, email)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (tercero_id, data['nombre'], data.get('telf', ''), data.get('celular', ''), data.get('email', ''))
        else:
            return None
        return db_manager.execute_query(connection, query, params, fetch=False)