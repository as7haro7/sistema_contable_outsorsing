from flask import session
from models.database import db_manager
from datetime import date, datetime
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class LibroModel:

    @staticmethod
    def get_libro_diario(fecha_desde, fecha_hasta, cuenta=None, tipo_asiento=None):
        """
        Obtener libro diario con filtros opcionales (multiempresa)
        
        Args:
            fecha_desde: Fecha inicial del rango
            fecha_hasta: Fecha final del rango
            cuenta: Código de cuenta específica (opcional)
            tipo_asiento: Tipo de asiento (opcional)
        
        Returns:
            Lista de registros del libro diario ordenados cronológicamente
        """
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            
            # Query base
            query = """
                SELECT 
                    a.codigo, 
                    a.fecha, 
                    a.glosa, 
                    a.tipo,
                    ta.descrip as tipo_descrip,
                    a.secuencia,
                    ad.id as detalle_id,
                    ad.cuenta, 
                    p.descrip as cuenta_descrip,
                    p.tipo_cuenta,
                    ad.debebs, 
                    ad.haberbs, 
                    ad.debesus, 
                    ad.habersus,
                    ad.referencia,
                    ad.cencosto,
                    cc.descrip as cencosto_descrip,
                    ad.orden,
                    a.usuario,
                    a.fechasys
                FROM Asiento a
                JOIN Asiento_det ad ON a.codigo = ad.cod_asiento
                JOIN Plancuenta p ON ad.cuenta = p.cuenta
                JOIN TipoAsiento ta ON a.tipo = ta.codigo
                LEFT JOIN CenCostos cc ON ad.cencosto = cc.codigo
                WHERE a.fecha BETWEEN %s AND %s 
                  AND a.estado = 'CONFIRMADO'
            """
            
            params = [fecha_desde, fecha_hasta]
            
            # Filtros opcionales
            if cuenta:
                query += " AND ad.cuenta = %s"
                params.append(cuenta)
            
            if tipo_asiento:
                query += " AND a.tipo = %s"
                params.append(tipo_asiento)
            
            query += " ORDER BY a.fecha, a.codigo, ad.orden"
            
            result = db_manager.execute_query(conn, query, params)
            
            # Procesar resultados para agrupar por asiento
            asientos_dict = {}
            for row in result:
                codigo = row['codigo']
                if codigo not in asientos_dict:
                    asientos_dict[codigo] = {
                        'codigo': row['codigo'],
                        'fecha': row['fecha'],
                        'glosa': row['glosa'],
                        'tipo': row['tipo'],
                        'tipo_descrip': row['tipo_descrip'],
                        'secuencia': row['secuencia'],
                        'usuario': row['usuario'],
                        'fechasys': row['fechasys'],
                        'detalles': [],
                        'total_debe_bs': Decimal('0.00'),
                        'total_haber_bs': Decimal('0.00'),
                        'total_debe_sus': Decimal('0.00'),
                        'total_haber_sus': Decimal('0.00')
                    }
                
                # Agregar detalle
                detalle = {
                    'detalle_id': row['detalle_id'],
                    'cuenta': row['cuenta'],
                    'cuenta_descrip': row['cuenta_descrip'],
                    'tipo_cuenta': row['tipo_cuenta'],
                    'debebs': row['debebs'] or Decimal('0.00'),
                    'haberbs': row['haberbs'] or Decimal('0.00'),
                    'debesus': row['debesus'] or Decimal('0.00'),
                    'habersus': row['habersus'] or Decimal('0.00'),
                    'referencia': row['referencia'],
                    'cencosto': row['cencosto'],
                    'cencosto_descrip': row['cencosto_descrip'],
                    'orden': row['orden']
                }
                
                asientos_dict[codigo]['detalles'].append(detalle)
                
                # Acumular totales
                asientos_dict[codigo]['total_debe_bs'] += detalle['debebs']
                asientos_dict[codigo]['total_haber_bs'] += detalle['haberbs']
                asientos_dict[codigo]['total_debe_sus'] += detalle['debesus']
                asientos_dict[codigo]['total_haber_sus'] += detalle['habersus']
            
            # Convertir a lista ordenada
            asientos_list = list(asientos_dict.values())
            asientos_list.sort(key=lambda x: (x['fecha'], x['codigo']))
            
            return asientos_list
            
        except Exception as e:
            logger.error(f"Error al obtener libro diario: {e}")
            return []

    @staticmethod
    def get_libro_mayor(fecha_desde, fecha_hasta, cuenta=None, solo_con_movimientos=True):
        """
        Obtener libro mayor agrupado por cuenta (multiempresa)
        
        Args:
            fecha_desde: Fecha inicial del rango
            fecha_hasta: Fecha final del rango
            cuenta: Código de cuenta específica (opcional)
            solo_con_movimientos: Si True, solo muestra cuentas con movimientos
        
        Returns:
            Diccionario con cuentas y sus movimientos
        """
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            
            query = """
                SELECT 
                    ad.cuenta, 
                    p.descrip as cuenta_descrip,
                    p.tipo_cuenta,
                    p.nivel,
                    p.moneda,
                    a.fecha, 
                    a.codigo, 
                    a.glosa,
                    a.tipo,
                    ta.descrip as tipo_descrip,
                    ad.debebs, 
                    ad.haberbs, 
                    ad.debesus, 
                    ad.habersus,
                    ad.referencia,
                    ad.cencosto,
                    cc.descrip as cencosto_descrip,
                    a.secuencia
                FROM Asiento a
                JOIN Asiento_det ad ON a.codigo = ad.cod_asiento
                JOIN Plancuenta p ON ad.cuenta = p.cuenta
                JOIN TipoAsiento ta ON a.tipo = ta.codigo
                LEFT JOIN CenCostos cc ON ad.cencosto = cc.codigo
                WHERE a.fecha BETWEEN %s AND %s 
                  AND a.estado = 'CONFIRMADO'
                  AND p.activo = TRUE
            """
            
            params = [fecha_desde, fecha_hasta]
            
            if cuenta:
                query += " AND ad.cuenta = %s"
                params.append(cuenta)
            
            query += " ORDER BY ad.cuenta, a.fecha, a.codigo, ad.orden"
            
            result = db_manager.execute_query(conn, query, params)
            
            # Procesar resultados para agrupar por cuenta
            cuentas_dict = {}
            for row in result:
                cuenta_codigo = row['cuenta']
                if cuenta_codigo not in cuentas_dict:
                    cuentas_dict[cuenta_codigo] = {
                        'cuenta': row['cuenta'],
                        'cuenta_descrip': row['cuenta_descrip'],
                        'tipo_cuenta': row['tipo_cuenta'],
                        'nivel': row['nivel'],
                        'moneda': row['moneda'],
                        'movimientos': [],
                        'saldo_inicial_bs': Decimal('0.00'),
                        'saldo_inicial_sus': Decimal('0.00'),
                        'total_debe_bs': Decimal('0.00'),
                        'total_haber_bs': Decimal('0.00'),
                        'total_debe_sus': Decimal('0.00'),
                        'total_haber_sus': Decimal('0.00'),
                        'saldo_final_bs': Decimal('0.00'),
                        'saldo_final_sus': Decimal('0.00')
                    }
                
                # Agregar movimiento
                movimiento = {
                    'fecha': row['fecha'],
                    'codigo': row['codigo'],
                    'glosa': row['glosa'],
                    'tipo': row['tipo'],
                    'tipo_descrip': row['tipo_descrip'],
                    'debebs': row['debebs'] or Decimal('0.00'),
                    'haberbs': row['haberbs'] or Decimal('0.00'),
                    'debesus': row['debesus'] or Decimal('0.00'),
                    'habersus': row['habersus'] or Decimal('0.00'),
                    'referencia': row['referencia'],
                    'cencosto': row['cencosto'],
                    'cencosto_descrip': row['cencosto_descrip'],
                    'secuencia': row['secuencia']
                }
                
                cuentas_dict[cuenta_codigo]['movimientos'].append(movimiento)
                
                # Acumular totales
                cuentas_dict[cuenta_codigo]['total_debe_bs'] += movimiento['debebs']
                cuentas_dict[cuenta_codigo]['total_haber_bs'] += movimiento['haberbs']
                cuentas_dict[cuenta_codigo]['total_debe_sus'] += movimiento['debesus']
                cuentas_dict[cuenta_codigo]['total_haber_sus'] += movimiento['habersus']
            
            # Calcular saldos finales
            for cuenta_data in cuentas_dict.values():
                cuenta_data['saldo_final_bs'] = cuenta_data['total_debe_bs'] - cuenta_data['total_haber_bs']
                cuenta_data['saldo_final_sus'] = cuenta_data['total_debe_sus'] - cuenta_data['total_haber_sus']
            
            # Si no se requieren cuentas sin movimientos, filtrar las vacías
            if solo_con_movimientos:
                cuentas_dict = {k: v for k, v in cuentas_dict.items() if v['movimientos']}
            
            return cuentas_dict
            
        except Exception as e:
            logger.error(f"Error al obtener libro mayor: {e}")
            return {}

    @staticmethod
    def get_saldos_iniciales(fecha_hasta, cuentas=None):
        """
        Obtener saldos iniciales de cuentas hasta una fecha determinada
        
        Args:
            fecha_hasta: Fecha límite para calcular saldos
            cuentas: Lista de cuentas específicas (opcional)
        
        Returns:
            Diccionario con saldos iniciales por cuenta
        """
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            
            query = """
                SELECT 
                    ad.cuenta,
                    p.descrip as cuenta_descrip,
                    p.tipo_cuenta,
                    SUM(ad.debebs) as total_debe_bs,
                    SUM(ad.haberbs) as total_haber_bs,
                    SUM(ad.debesus) as total_debe_sus,
                    SUM(ad.habersus) as total_haber_sus,
                    (SUM(ad.debebs) - SUM(ad.haberbs)) as saldo_bs,
                    (SUM(ad.debesus) - SUM(ad.habersus)) as saldo_sus
                FROM Asiento_det ad
                JOIN Asiento a ON ad.cod_asiento = a.codigo
                JOIN Plancuenta p ON ad.cuenta = p.cuenta
                WHERE a.fecha <= %s
                  AND a.estado = 'CONFIRMADO'
                  AND p.activo = TRUE
            """
            
            params = [fecha_hasta]
            
            if cuentas:
                placeholders = ','.join(['%s'] * len(cuentas))
                query += f" AND ad.cuenta IN ({placeholders})"
                params.extend(cuentas)
            
            query += """
                GROUP BY ad.cuenta, p.descrip, p.tipo_cuenta
                HAVING SUM(ad.debebs) > 0 OR SUM(ad.haberbs) > 0
                ORDER BY ad.cuenta
            """
            
            return db_manager.execute_query(conn, query, params)
            
        except Exception as e:
            logger.error(f"Error al obtener saldos iniciales: {e}")
            return []

    @staticmethod
    def get_balance_general(fecha_hasta=None, moneda='BOB'):
        """Obtener balance general al corte"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            if not fecha_hasta:
                fecha_hasta = date.today()
            query = "SELECT * FROM balance_general(%s, %s, %s)"
            return db_manager.execute_query(conn, query, (fecha_hasta, moneda, empresa_id))
        except Exception as e:
            logger.error(f"Error al obtener balance general: {e}")
            return []

    @staticmethod
    def get_estado_resultados(fecha_desde, fecha_hasta, moneda='BOB'):
        """Obtener estado de resultados"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT 
                    p.cuenta, 
                    p.descrip, 
                    p.tipo_cuenta,
                    p.nivel,
                    CASE 
                        WHEN %s = 'BOB' THEN COALESCE(SUM(ad.haberbs - ad.debebs), 0)
                        ELSE COALESCE(SUM(ad.habersus - ad.debesus), 0)
                    END as saldo
                FROM Plancuenta p
                LEFT JOIN Asiento_det ad ON p.cuenta = ad.cuenta
                LEFT JOIN Asiento a ON ad.cod_asiento = a.codigo
                WHERE p.activo = TRUE 
                  AND p.tipo_cuenta IN ('INGRESOS', 'EGRESO', 'COSTOS')
                  AND (a.fecha IS NULL OR (a.fecha BETWEEN %s AND %s AND a.estado = 'CONFIRMADO'))
                GROUP BY p.cuenta, p.descrip, p.tipo_cuenta, p.nivel
                ORDER BY p.cuenta
            """
            return db_manager.execute_query(conn, query, (moneda, fecha_desde, fecha_hasta))
        except Exception as e:
            logger.error(f"Error al obtener estado de resultados: {e}")
            return []

    @staticmethod
    def get_balance_comprobacion(fecha_desde, fecha_hasta):
        """Obtener balance de comprobación"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT 
                    ad.cuenta,
                    pc.descrip as cuenta_descrip,
                    pc.tipo_cuenta,
                    pc.nivel,
                    SUM(ad.debebs) as total_debe_bs,
                    SUM(ad.haberbs) as total_haber_bs,
                    SUM(ad.debesus) as total_debe_sus,
                    SUM(ad.habersus) as total_haber_sus,
                    (SUM(ad.debebs) - SUM(ad.haberbs)) as saldo_bs,
                    (SUM(ad.debesus) - SUM(ad.habersus)) as saldo_sus
                FROM Asiento_det ad
                JOIN Asiento a ON ad.cod_asiento = a.codigo
                JOIN Plancuenta pc ON ad.cuenta = pc.cuenta
                WHERE a.fecha BETWEEN %s AND %s
                  AND a.estado = 'CONFIRMADO'
                  AND pc.activo = TRUE
                GROUP BY ad.cuenta, pc.descrip, pc.tipo_cuenta, pc.nivel
                HAVING SUM(ad.debebs) > 0 OR SUM(ad.haberbs) > 0
                ORDER BY ad.cuenta
            """
            return db_manager.execute_query(conn, query, (fecha_desde, fecha_hasta))
        except Exception as e:
            logger.error(f"Error al obtener balance de comprobación: {e}")
            return []

    @staticmethod
    def get_tipos_asiento():
        """Obtener tipos de asiento disponibles"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT codigo, descrip, activo
                FROM TipoAsiento 
                WHERE activo = TRUE
                ORDER BY descrip
            """
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener tipos de asiento: {e}")
            return []

    @staticmethod
    def get_cuentas_con_movimientos(fecha_desde, fecha_hasta):
        """Obtener lista de cuentas que tienen movimientos en el período"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT DISTINCT 
                    ad.cuenta,
                    p.descrip as cuenta_descrip,
                    p.tipo_cuenta
                FROM Asiento_det ad
                JOIN Asiento a ON ad.cod_asiento = a.codigo
                JOIN Plancuenta p ON ad.cuenta = p.cuenta
                WHERE a.fecha BETWEEN %s AND %s
                  AND a.estado = 'CONFIRMADO'
                  AND p.activo = TRUE
                ORDER BY ad.cuenta
            """
            return db_manager.execute_query(conn, query, (fecha_desde, fecha_hasta))
        except Exception as e:
            logger.error(f"Error al obtener cuentas con movimientos: {e}")
            return []

    @staticmethod
    def get_resumen_periodo(fecha_desde, fecha_hasta):
        """Obtener resumen de movimientos del período"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT 
                    COUNT(DISTINCT a.codigo) as total_asientos,
                    COUNT(ad.id) as total_movimientos,
                    SUM(ad.debebs) as total_debe_bs,
                    SUM(ad.haberbs) as total_haber_bs,
                    SUM(ad.debesus) as total_debe_sus,
                    SUM(ad.habersus) as total_haber_sus,
                    COUNT(DISTINCT ad.cuenta) as cuentas_afectadas,
                    MIN(a.fecha) as primera_fecha,
                    MAX(a.fecha) as ultima_fecha
                FROM Asiento a
                JOIN Asiento_det ad ON a.codigo = ad.cod_asiento
                WHERE a.fecha BETWEEN %s AND %s
                  AND a.estado = 'CONFIRMADO'
            """
            result = db_manager.execute_query(conn, query, (fecha_desde, fecha_hasta))
            return result[0] if result else {}
        except Exception as e:
            logger.error(f"Error al obtener resumen del período: {e}")
            return {}