from flask import session
from models.database import db_manager

class ReporteModel:
    @staticmethod
    def get_periodos():
        """Obtener todos los periodos contables"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT * FROM periodos
            ORDER BY fecha_inicio DESC
        """
        
        return db_manager.execute_query(connection, query)
    
    @staticmethod
    def get_periodo_actual():
        """Obtener el periodo contable actual"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT * FROM periodos
            WHERE estado = 'ABIERTO'
            ORDER BY fecha_inicio DESC
            LIMIT 1
        """
        
        result = db_manager.execute_query(connection, query)
        return result[0] if result else None
    
    @staticmethod
    def get_resumen_asientos(periodo_id=None):
        """Obtener resumen de asientos contables"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT COUNT(*) as total_asientos,
                   SUM(CASE WHEN a.estado = 'ACTIVO' THEN 1 ELSE 0 END) as asientos_activos,
                   SUM(CASE WHEN a.estado = 'ANULADO' THEN 1 ELSE 0 END) as asientos_anulados
            FROM asientos a
        """
        
        params = []
        if periodo_id:
            query += " WHERE a.periodo_id = %s"
            params.append(periodo_id)
        
        result = db_manager.execute_query(connection, query, tuple(params) if params else None)
        return result[0] if result else None
    
    @staticmethod
    def get_resumen_facturas(periodo_id=None):
        """Obtener resumen de facturas"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        # Resumen de facturas de compra
        compras_query = """
            SELECT COUNT(*) as total_facturas,
                   SUM(total) as total_monto,
                   SUM(credito_fiscal) as total_credito_fiscal
            FROM facturas_compras
        """
        
        params = []
        if periodo_id:
            compras_query += " WHERE periodo_id = %s"
            params.append(periodo_id)
        
        compras_result = db_manager.execute_query(connection, compras_query, tuple(params) if params else None)
        compras = compras_result[0] if compras_result else None
        
        # Resumen de facturas de venta
        ventas_query = """
            SELECT COUNT(*) as total_facturas,
                   SUM(CASE WHEN estado != 'ANULADA' THEN total ELSE 0 END) as total_monto,
                   SUM(CASE WHEN estado != 'ANULADA' THEN debito_fiscal ELSE 0 END) as total_debito_fiscal,
                   SUM(CASE WHEN estado = 'ANULADA' THEN 1 ELSE 0 END) as facturas_anuladas
            FROM facturas_ventas
        """
        
        params = []
        if periodo_id:
            ventas_query += " WHERE periodo_id = %s"
            params.append(periodo_id)
        
        ventas_result = db_manager.execute_query(connection, ventas_query, tuple(params) if params else None)
        ventas = ventas_result[0] if ventas_result else None
        
        return {
            'compras': compras,
            'ventas': ventas
        }
    
    @staticmethod
    def get_resumen_cuentas():
        """Obtener resumen de cuentas contables"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT t.codigo, t.descrip,
                   COUNT(p.cuenta) as total_cuentas
            FROM tipocuenta t
            LEFT JOIN plancuenta p ON t.codigo = p.tipo_cuenta
            GROUP BY t.codigo, t.descrip
            ORDER BY t.codigo
        """
        
        return db_manager.execute_query(connection, query)
    
    @staticmethod
    def get_top_clientes(limite=5):
        """Obtener los principales clientes por monto de facturación"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT c.id, c.nombre, c.nit,
                   COUNT(f.id) as total_facturas,
                   SUM(f.total) as total_monto
            FROM clientes c
            JOIN facturas_ventas f ON c.nit = f.nit
            WHERE f.estado != 'ANULADA'
            GROUP BY c.id, c.nombre, c.nit
            ORDER BY total_monto DESC
            LIMIT %s
        """
        
        return db_manager.execute_query(connection, query, (limite,))
    
    @staticmethod
    def get_top_proveedores(limite=5):
        """Obtener los principales proveedores por monto de compras"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT p.id, p.nombre, p.nit,
                   COUNT(f.id) as total_facturas,
                   SUM(f.total) as total_monto
            FROM proveedores p
            JOIN facturas_compras f ON p.nit = f.nit
            GROUP BY p.id, p.nombre, p.nit
            ORDER BY total_monto DESC
            LIMIT %s
        """
        
        return db_manager.execute_query(connection, query, (limite,))
    


    