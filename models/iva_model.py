from flask import session
from models.database import db_manager

class IvaModel:
    @staticmethod
    def get_facturas_compras(periodo_id=None, fecha_inicio=None, fecha_fin=None):
        """Obtener facturas de compras para libro de compras"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT f.id, f.fecha, f.nit, f.razon_social, f.nro_factura, f.nro_autorizacion,
                   f.codigo_control, f.total, f.ice, f.exentas, f.tasa_cero, f.subtotal,
                   f.descuentos, f.importe_base, f.credito_fiscal, f.tipo_compra
            FROM facturas_compras f
            WHERE 1=1
        """
        
        params = []
        
        if periodo_id:
            query += " AND f.periodo_id = %s"
            params.append(periodo_id)
        
        if fecha_inicio:
            query += " AND f.fecha >= %s"
            params.append(fecha_inicio)
            
        if fecha_fin:
            query += " AND f.fecha <= %s"
            params.append(fecha_fin)
        
        query += " ORDER BY f.fecha, f.nro_factura"
        
        return db_manager.execute_query(connection, query, tuple(params) if params else None)
    
    @staticmethod
    def get_facturas_ventas(periodo_id=None, fecha_inicio=None, fecha_fin=None):
        """Obtener facturas de ventas para libro de ventas"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        query = """
            SELECT f.id, f.fecha, f.nit, f.razon_social, f.nro_factura, f.nro_autorizacion,
                   f.codigo_control, f.total, f.ice, f.exentas, f.tasa_cero, f.subtotal,
                   f.descuentos, f.importe_base, f.debito_fiscal, f.estado
            FROM facturas_ventas f
            WHERE f.estado != 'ANULADA'
        """
        
        params = []
        
        if periodo_id:
            query += " AND f.periodo_id = %s"
            params.append(periodo_id)
        
        if fecha_inicio:
            query += " AND f.fecha >= %s"
            params.append(fecha_inicio)
            
        if fecha_fin:
            query += " AND f.fecha <= %s"
            params.append(fecha_fin)
        
        query += " ORDER BY f.fecha, f.nro_factura"
        
        return db_manager.execute_query(connection, query, tuple(params) if params else None)
    
    @staticmethod
    def get_resumen_iva(periodo_id=None):
        """Obtener resumen de IVA para un periodo"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        # Obtener total crédito fiscal
        credito_query = """
            SELECT SUM(credito_fiscal) as total_credito_fiscal
            FROM facturas_compras
            WHERE 1=1
        """
        
        params = []
        if periodo_id:
            credito_query += " AND periodo_id = %s"
            params.append(periodo_id)
        
        credito_result = db_manager.execute_query(connection, credito_query, tuple(params) if params else None)
        total_credito = credito_result[0]['total_credito_fiscal'] if credito_result and credito_result[0]['total_credito_fiscal'] else 0
        
        # Obtener total débito fiscal
        debito_query = """
            SELECT SUM(debito_fiscal) as total_debito_fiscal
            FROM facturas_ventas
            WHERE estado != 'ANULADA'
        """
        
        params = []
        if periodo_id:
            debito_query += " AND periodo_id = %s"
            params.append(periodo_id)
        
        debito_result = db_manager.execute_query(connection, debito_query, tuple(params) if params else None)
        total_debito = debito_result[0]['total_debito_fiscal'] if debito_result and debito_result[0]['total_debito_fiscal'] else 0
        
        # Calcular saldo a favor o a pagar
        saldo = total_debito - total_credito
        
        return {
            'total_credito_fiscal': total_credito,
            'total_debito_fiscal': total_debito,
            'saldo': saldo,
            'tipo_saldo': 'PAGAR' if saldo > 0 else 'FAVOR'
        }
    
    @staticmethod
    def exportar_libro_compras(periodo_id=None, fecha_inicio=None, fecha_fin=None, formato='txt'):
        """Exportar libro de compras en formato TXT o Excel"""
        # Esta función generaría el archivo de exportación
        # Aquí solo se obtienen los datos
        facturas = IvaModel.get_facturas_compras(periodo_id, fecha_inicio, fecha_fin)
        return facturas
    
    @staticmethod
    def exportar_libro_ventas(periodo_id=None, fecha_inicio=None, fecha_fin=None, formato='txt'):
        """Exportar libro de ventas en formato TXT o Excel"""
        # Esta función generaría el archivo de exportación
        # Aquí solo se obtienen los datos
        facturas = IvaModel.get_facturas_ventas(periodo_id, fecha_inicio, fecha_fin)
        return facturas