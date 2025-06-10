from flask import session
from models.database import db_manager

class EstadoModel:
    @staticmethod
    def get_balance_general(periodo_id=None, fecha_corte=None):
        """Obtener datos para el balance general"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        # Obtener cuentas de activo, pasivo y patrimonio
        query = """
            SELECT p.cuenta, p.descrip, p.tipo_cuenta, p.nivel, p.tipomov,
                   t.descrip as tipo_descripcion,
                   COALESCE(SUM(CASE WHEN d.tipo_mov = 'D' THEN d.monto_bs ELSE 0 END), 0) as total_debe,
                   COALESCE(SUM(CASE WHEN d.tipo_mov = 'H' THEN d.monto_bs ELSE 0 END), 0) as total_haber
            FROM plancuenta p
            LEFT JOIN tipocuenta t ON p.tipo_cuenta = t.codigo
            LEFT JOIN asiento_detalles d ON p.cuenta = d.cuenta
            LEFT JOIN asientos a ON d.asiento_id = a.id AND a.estado = 'ACTIVO'
            WHERE p.tipo_cuenta IN ('A', 'P', 'C') -- Activo, Pasivo, Capital
        """
        
        params = []
        
        if periodo_id:
            query += " AND a.periodo_id = %s"
            params.append(periodo_id)
        
        if fecha_corte:
            query += " AND a.fecha <= %s"
            params.append(fecha_corte)
        
        query += " GROUP BY p.cuenta, p.descrip, p.tipo_cuenta, p.nivel, p.tipomov, t.descrip"
        query += " ORDER BY p.cuenta"
        
        return db_manager.execute_query(connection, query, tuple(params) if params else None)
    
    @staticmethod
    def get_estado_resultados(periodo_id=None, fecha_inicio=None, fecha_fin=None):
        """Obtener datos para el estado de resultados"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        # Obtener cuentas de ingresos y egresos
        query = """
            SELECT p.cuenta, p.descrip, p.tipo_cuenta, p.nivel, p.tipomov,
                   t.descrip as tipo_descripcion,
                   COALESCE(SUM(CASE WHEN d.tipo_mov = 'D' THEN d.monto_bs ELSE 0 END), 0) as total_debe,
                   COALESCE(SUM(CASE WHEN d.tipo_mov = 'H' THEN d.monto_bs ELSE 0 END), 0) as total_haber
            FROM plancuenta p
            LEFT JOIN tipocuenta t ON p.tipo_cuenta = t.codigo
            LEFT JOIN asiento_detalles d ON p.cuenta = d.cuenta
            LEFT JOIN asientos a ON d.asiento_id = a.id AND a.estado = 'ACTIVO'
            WHERE p.tipo_cuenta IN ('I', 'E') -- Ingresos, Egresos
        """
        
        params = []
        
        if periodo_id:
            query += " AND a.periodo_id = %s"
            params.append(periodo_id)
        
        if fecha_inicio:
            query += " AND a.fecha >= %s"
            params.append(fecha_inicio)
            
        if fecha_fin:
            query += " AND a.fecha <= %s"
            params.append(fecha_fin)
        
        query += " GROUP BY p.cuenta, p.descrip, p.tipo_cuenta, p.nivel, p.tipomov, t.descrip"
        query += " ORDER BY p.cuenta"
        
        return db_manager.execute_query(connection, query, tuple(params) if params else None)
    
    @staticmethod
    def get_flujo_efectivo(periodo_id=None, fecha_inicio=None, fecha_fin=None):
        """Obtener datos para el flujo de efectivo"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        # Obtener movimientos de cuentas de efectivo y equivalentes
        query = """
            SELECT a.fecha, a.numero, a.glosa,
                   d.cuenta, p.descrip as cuenta_nombre, d.tipo_mov,
                   d.monto_bs, d.glosa as detalle_glosa
            FROM asientos a
            JOIN asiento_detalles d ON a.id = d.asiento_id
            JOIN plancuenta p ON d.cuenta = p.cuenta
            WHERE a.estado = 'ACTIVO'
            AND p.cuenta LIKE '11%' -- Cuentas de efectivo y equivalentes (ajustar según plan de cuentas)
        """
        
        params = []
        
        if periodo_id:
            query += " AND a.periodo_id = %s"
            params.append(periodo_id)
        
        if fecha_inicio:
            query += " AND a.fecha >= %s"
            params.append(fecha_inicio)
            
        if fecha_fin:
            query += " AND a.fecha <= %s"
            params.append(fecha_fin)
        
        query += " ORDER BY a.fecha, a.numero"
        
        return db_manager.execute_query(connection, query, tuple(params) if params else None)
    
    @staticmethod
    def get_cambios_patrimonio(periodo_id=None, fecha_inicio=None, fecha_fin=None):
        """Obtener datos para el estado de cambios en el patrimonio"""
        connection = db_manager.get_company_connection(session['empresa_id'])
        
        # Obtener movimientos de cuentas de patrimonio
        query = """
            SELECT a.fecha, a.numero, a.glosa,
                   d.cuenta, p.descrip as cuenta_nombre, d.tipo_mov,
                   d.monto_bs, d.glosa as detalle_glosa
            FROM asientos a
            JOIN asiento_detalles d ON a.id = d.asiento_id
            JOIN plancuenta p ON d.cuenta = p.cuenta
            WHERE a.estado = 'ACTIVO'
            AND p.tipo_cuenta = 'C' -- Cuentas de capital/patrimonio
        """
        
        params = []
        
        if periodo_id:
            query += " AND a.periodo_id = %s"
            params.append(periodo_id)
        
        if fecha_inicio:
            query += " AND a.fecha >= %s"
            params.append(fecha_inicio)
            
        if fecha_fin:
            query += " AND a.fecha <= %s"
            params.append(fecha_fin)
        
        query += " ORDER BY a.fecha, a.numero"
        
        return db_manager.execute_query(connection, query, tuple(params) if params else None)