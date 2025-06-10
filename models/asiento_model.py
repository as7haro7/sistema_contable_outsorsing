

from models.database import db_manager
import logging
from datetime import datetime
from flask import session 
logger = logging.getLogger(__name__)

class AsientoModel:

    @staticmethod
    def obtener_tipos_asiento():
        """Devuelve los tipos de asiento disponibles"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT codigo, descrip FROM TipoAsiento WHERE activo = TRUE ORDER BY codigo"
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener tipos de asiento: {e}")
            return []

    @staticmethod
    def obtener_asientos(filtro=None):
        """Consulta asientos contables, opcionalmente con filtro"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            base_query = """
                SELECT a.codigo, a.cta, a.tipo, a.secuencia, a.srs, 
                       a.debebs, a.haberbs, a.debesus, a.habersus,
                       a.glosa, a.fecha, a.estado, a.usuario, a.fechasys,
                       a.usuario_confirmacion, a.fecha_confirmacion,
                       ta.descrip as tipo_descrip
                FROM Asiento a
                LEFT JOIN TipoAsiento ta ON a.tipo = ta.codigo
            """
            
            # Aplicar filtros si se proporcionan
            where_conditions = []
            params = []
            
            if filtro:
                if filtro.get('fecha_desde'):
                    where_conditions.append("a.fecha >= %s")
                    params.append(filtro['fecha_desde'])
                
                if filtro.get('fecha_hasta'):
                    where_conditions.append("a.fecha <= %s")
                    params.append(filtro['fecha_hasta'])
                
                if filtro.get('tipo'):
                    where_conditions.append("a.tipo = %s")
                    params.append(filtro['tipo'])
                
                if filtro.get('estado'):
                    where_conditions.append("a.estado = %s")
                    params.append(filtro['estado'])
                
                if filtro.get('codigo'):
                    where_conditions.append("a.codigo ILIKE %s")
                    params.append(f"%{filtro['codigo']}%")
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            base_query += " ORDER BY a.fecha DESC, a.codigo DESC"
            
            return db_manager.execute_query(conn, base_query, params if params else None)
        except Exception as e:
            logger.error(f"Error al obtener asientos: {e}")
            return []

    @staticmethod
    def obtener_asiento_por_codigo(codigo):
        """Obtiene un asiento y sus detalles"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            
            # Obtener asiento principal
            query = """
                SELECT a.codigo, a.cta, a.tipo, a.secuencia, a.srs, 
                       a.debebs, a.haberbs, a.debesus, a.habersus,
                       a.glosa, a.fecha, a.estado, a.usuario, a.fechasys,
                       a.usuario_confirmacion, a.fecha_confirmacion,
                       ta.descrip as tipo_descrip
                FROM Asiento a
                LEFT JOIN TipoAsiento ta ON a.tipo = ta.codigo
                WHERE a.codigo = %s
            """
            asiento = db_manager.execute_query(conn, query, (codigo,))
            
            if not asiento:
                return None
            
            # Obtener detalles del asiento
            query_det = """
                SELECT ad.id, ad.cod_asiento, ad.cuenta, ad.item,
                       ad.debebs, ad.haberbs, ad.debesus, ad.habersus,
                       ad.cencosto, ad.referencia, ad.orden,
                       pc.descrip as cuenta_descrip,
                       cc.descrip as cencosto_descrip
                FROM Asiento_det ad
                LEFT JOIN Plancuenta pc ON ad.cuenta = pc.cuenta
                LEFT JOIN CenCostos cc ON ad.cencosto = cc.codigo
                WHERE ad.cod_asiento = %s
                ORDER BY ad.orden, ad.id
            """
            detalles = db_manager.execute_query(conn, query_det, (codigo,))
            
            return {'asiento': asiento[0], 'detalles': detalles}
        except Exception as e:
            logger.error(f"Error al obtener asiento {codigo}: {e}")
            return None

    @staticmethod
    def generar_codigo_asiento(tipo, fecha=None):
        """Genera un código único para el asiento"""
        try:
            if fecha is None:
                fecha = datetime.now().date()
            
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            
            # Formato: TIPO-YYYYMMDD-NNNN
            fecha_str = fecha.strftime('%Y%m%d')
            prefijo = f"{tipo}-{fecha_str}-"
            
            # Buscar el último número de secuencia para este prefijo
            query = """
                SELECT codigo FROM Asiento 
                WHERE codigo LIKE %s 
                ORDER BY codigo DESC 
                LIMIT 1
            """
            resultado = db_manager.execute_query(conn, query, (f"{prefijo}%",))
            
            if resultado:
                ultimo_codigo = resultado[0]['codigo']
                # Extraer el número de secuencia
                secuencia = int(ultimo_codigo.split('-')[-1]) + 1
            else:
                secuencia = 1
            
            return f"{prefijo}{secuencia:04d}"
        except Exception as e:
            logger.error(f"Error al generar código de asiento: {e}")
            return None

    @staticmethod
    def validar_partida_doble(detalles):
        """Valida que se cumpla la partida doble"""
        try:
            suma_debe_bs = sum(float(d.get('debebs', 0)) for d in detalles)
            suma_haber_bs = sum(float(d.get('haberbs', 0)) for d in detalles)
            suma_debe_sus = sum(float(d.get('debesus', 0)) for d in detalles)
            suma_haber_sus = sum(float(d.get('habersus', 0)) for d in detalles)
            
            # Verificar partida doble en ambas monedas
            if round(suma_debe_bs, 2) != round(suma_haber_bs, 2):
                return False, f"No se cumple partida doble en Bs.: Debe={suma_debe_bs:.2f}, Haber={suma_haber_bs:.2f}"
            
            if round(suma_debe_sus, 2) != round(suma_haber_sus, 2):
                return False, f"No se cumple partida doble en $us: Debe={suma_debe_sus:.2f}, Haber={suma_haber_sus:.2f}"
            
            # Verificar que haya al menos un movimiento
            if suma_debe_bs == 0 and suma_haber_bs == 0:
                return False, "El asiento debe tener al menos un movimiento"
            
            return True, "Partida doble válida"
        except Exception as e:
            logger.error(f"Error al validar partida doble: {e}")
            return False, f"Error en validación: {str(e)}"

    @staticmethod
    def crear_asiento(data, detalles, usuario):
        """
        Crea un asiento contable y sus detalles.
        data: dict con los campos de Asiento
        detalles: lista de dicts con los campos de Asiento_det
        """
        conn = None
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            conn.autocommit = False  # Iniciar transacción
            
            # Validar partida doble
            es_valida, mensaje = AsientoModel.validar_partida_doble(detalles)
            if not es_valida:
                return {'success': False, 'message': mensaje}
            
            # Generar código si no se proporciona
            if not data.get('codigo'):
                data['codigo'] = AsientoModel.generar_codigo_asiento(data['tipo'], data.get('fecha'))
                if not data['codigo']:
                    return {'success': False, 'message': 'Error al generar código de asiento'}
            
            # Verificar que el código no exista
            query_existe = "SELECT codigo FROM Asiento WHERE codigo = %s"
            existe = db_manager.execute_query(conn, query_existe, (data['codigo'],))
            if existe:
                return {'success': False, 'message': f'Ya existe un asiento con código {data["codigo"]}'}
            
            # Calcular totales
            total_debe_bs = sum(float(d.get('debebs', 0)) for d in detalles)
            total_haber_bs = sum(float(d.get('haberbs', 0)) for d in detalles)
            total_debe_sus = sum(float(d.get('debesus', 0)) for d in detalles)
            total_haber_sus = sum(float(d.get('habersus', 0)) for d in detalles)
            
            # Insertar asiento principal
            query = """
                INSERT INTO Asiento (codigo, cta, tipo, secuencia, srs, 
                                   debebs, haberbs, debesus, habersus,
                                   glosa, fecha, estado, usuario, fechasys)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            params = (
                data['codigo'],
                data.get('cta'),
                data['tipo'],
                data.get('secuencia', 0),
                data.get('srs'),
                total_debe_bs,
                total_haber_bs,
                total_debe_sus,
                total_haber_sus,
                data['glosa'],
                data['fecha'],
                data.get('estado', 'BORRADOR'),
                usuario
            )
            db_manager.execute_query(conn, query, params, fetch=False)
            
            # Insertar detalles
            for i, det in enumerate(detalles, 1):
                # Validar que la cuenta exista
                query_cuenta = "SELECT cuenta FROM Plancuenta WHERE cuenta = %s AND activo = TRUE"
                cuenta_existe = db_manager.execute_query(conn, query_cuenta, (det['cuenta'],))
                if not cuenta_existe:
                    conn.rollback()
                    return {'success': False, 'message': f'La cuenta {det["cuenta"]} no existe o está inactiva'}
                
                query_det = """
                    INSERT INTO Asiento_det (cod_asiento, cuenta, item, 
                                           debebs, haberbs, debesus, habersus,
                                           cencosto, referencia, orden)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params_det = (
                    data['codigo'],
                    det['cuenta'],
                    det.get('item'),
                    det.get('debebs', 0),
                    det.get('haberbs', 0),
                    det.get('debesus', 0),
                    det.get('habersus', 0),
                    det.get('cencosto'),
                    det.get('referencia'),
                    det.get('orden', i)
                )
                db_manager.execute_query(conn, query_det, params_det, fetch=False)
            
            conn.commit()
            return {'success': True, 'message': 'Asiento creado correctamente', 'codigo': data['codigo']}
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error al crear asiento: {e}")
            return {'success': False, 'message': f'Error al crear asiento: {str(e)}'}
        finally:
            if conn:
                conn.autocommit = True

    @staticmethod
    def actualizar_asiento(codigo, data, detalles, usuario):
        """
        Edita un asiento y sus detalles (solo si no está confirmado)
        """
        conn = None
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            conn.autocommit = False  # Iniciar transacción
            
            # Verificar si el asiento existe y su estado
            query_estado = "SELECT estado FROM Asiento WHERE codigo = %s"
            resultado = db_manager.execute_query(conn, query_estado, (codigo,))
            if not resultado:
                return {'success': False, 'message': 'El asiento no existe'}
            
            estado = resultado[0]['estado']
            if estado != 'BORRADOR':
                return {'success': False, 'message': 'No se puede modificar un asiento confirmado o anulado'}
            
            # Validar partida doble
            es_valida, mensaje = AsientoModel.validar_partida_doble(detalles)
            if not es_valida:
                return {'success': False, 'message': mensaje}
            
            # Calcular totales
            total_debe_bs = sum(float(d.get('debebs', 0)) for d in detalles)
            total_haber_bs = sum(float(d.get('haberbs', 0)) for d in detalles)
            total_debe_sus = sum(float(d.get('debesus', 0)) for d in detalles)
            total_haber_sus = sum(float(d.get('habersus', 0)) for d in detalles)
            
            # Actualizar asiento principal
            query = """
                UPDATE Asiento
                SET cta=%s, tipo=%s, secuencia=%s, srs=%s,
                    debebs=%s, haberbs=%s, debesus=%s, habersus=%s,
                    glosa=%s, fecha=%s, usuario=%s, fechasys=NOW()
                WHERE codigo=%s
            """
            params = (
                data.get('cta'),
                data['tipo'],
                data.get('secuencia', 0),
                data.get('srs'),
                total_debe_bs,
                total_haber_bs,
                total_debe_sus,
                total_haber_sus,
                data['glosa'],
                data['fecha'],
                usuario,
                codigo
            )
            db_manager.execute_query(conn, query, params, fetch=False)
            
            # Eliminar detalles anteriores
            db_manager.execute_query(conn, "DELETE FROM Asiento_det WHERE cod_asiento=%s", (codigo,), fetch=False)
            
            # Insertar nuevos detalles
            for i, det in enumerate(detalles, 1):
                # Validar que la cuenta exista
                query_cuenta = "SELECT cuenta FROM Plancuenta WHERE cuenta = %s AND activo = TRUE"
                cuenta_existe = db_manager.execute_query(conn, query_cuenta, (det['cuenta'],))
                if not cuenta_existe:
                    conn.rollback()
                    return {'success': False, 'message': f'La cuenta {det["cuenta"]} no existe o está inactiva'}
                
                query_det = """
                    INSERT INTO Asiento_det (cod_asiento, cuenta, item,
                                           debebs, haberbs, debesus, habersus,
                                           cencosto, referencia, orden)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params_det = (
                    codigo,
                    det['cuenta'],
                    det.get('item'),
                    det.get('debebs', 0),
                    det.get('haberbs', 0),
                    det.get('debesus', 0),
                    det.get('habersus', 0),
                    det.get('cencosto'),
                    det.get('referencia'),
                    det.get('orden', i)
                )
                db_manager.execute_query(conn, query_det, params_det, fetch=False)
            
            conn.commit()
            return {'success': True, 'message': 'Asiento actualizado correctamente'}
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error al actualizar asiento: {e}")
            return {'success': False, 'message': f'Error al actualizar asiento: {str(e)}'}
        finally:
            if conn:
                conn.autocommit = True

    @staticmethod
    def confirmar_asiento(codigo, usuario):
        """Confirma un asiento (cambia estado a CONFIRMADO)"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            
            # Verificar que el asiento existe y está en borrador
            query_estado = "SELECT estado FROM Asiento WHERE codigo = %s"
            resultado = db_manager.execute_query(conn, query_estado, (codigo,))
            if not resultado:
                return {'success': False, 'message': 'El asiento no existe'}
            
            if resultado[0]['estado'] != 'BORRADOR':
                return {'success': False, 'message': 'Solo se pueden confirmar asientos en borrador'}
            
            # Cambiar estado a CONFIRMADO
            query = """
                UPDATE Asiento 
                SET estado='CONFIRMADO', usuario_confirmacion=%s, fecha_confirmacion=NOW()
                WHERE codigo=%s
            """
            db_manager.execute_query(conn, query, (usuario, codigo), fetch=False)
            
            return {'success': True, 'message': 'Asiento confirmado correctamente'}
        except Exception as e:
            logger.error(f"Error al confirmar asiento: {e}")
            return {'success': False, 'message': f'Error al confirmar asiento: {str(e)}'}

    @staticmethod
    def anular_asiento(codigo, usuario):
        """Anula un asiento (cambia estado a ANULADO si no está en libros oficiales)"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            
            # Verificar si el asiento está en libros oficiales
            query_libros = """
                SELECT 1 FROM LibroCompras WHERE asiento=%s
                UNION
                SELECT 1 FROM LibroVentas WHERE asiento=%s
            """
            en_libros = db_manager.execute_query(conn, query_libros, (codigo, codigo))
            if en_libros:
                return {'success': False, 'message': 'No se puede anular un asiento que ya está en libros oficiales'}
            
            # Verificar que el asiento existe
            query_existe = "SELECT estado FROM Asiento WHERE codigo = %s"
            resultado = db_manager.execute_query(conn, query_existe, (codigo,))
            if not resultado:
                return {'success': False, 'message': 'El asiento no existe'}
            
            if resultado[0]['estado'] == 'ANULADO':
                return {'success': False, 'message': 'El asiento ya está anulado'}
            
            # Cambiar estado a ANULADO
            query = """
                UPDATE Asiento 
                SET estado='ANULADO', usuario_confirmacion=%s, fecha_confirmacion=NOW()
                WHERE codigo=%s
            """
            db_manager.execute_query(conn, query, (usuario, codigo), fetch=False)
            
            return {'success': True, 'message': 'Asiento anulado correctamente'}
        except Exception as e:
            logger.error(f"Error al anular asiento: {e}")
            return {'success': False, 'message': f'Error al anular asiento: {str(e)}'}

    @staticmethod
    def obtener_cuentas_activas():
        """Obtiene las cuentas del plan de cuentas activas"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT cuenta, descrip, tipo_cuenta, nivel, tipomov, moneda
                FROM Plancuenta
                WHERE activo = TRUE
                ORDER BY cuenta
            """
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener cuentas: {e}")
            return []

    @staticmethod
    def obtener_centros_costos():
        """Obtiene los centros de costos activos"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT codigo, descrip
                FROM CenCostos
                WHERE activo = TRUE
                ORDER BY codigo
            """
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener centros de costos: {e}")
            return []

    @staticmethod
    def obtener_balance_comprobacion(fecha_desde, fecha_hasta):
        """Genera el balance de comprobación para un rango de fechas"""
        try:
            empresa_id = session.get('empresa_id')
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT 
                    ad.cuenta,
                    pc.descrip as cuenta_descrip,
                    pc.tipo_cuenta,
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
                GROUP BY ad.cuenta, pc.descrip, pc.tipo_cuenta
                HAVING SUM(ad.debebs) > 0 OR SUM(ad.haberbs) > 0
                ORDER BY ad.cuenta
            """
            return db_manager.execute_query(conn, query, (fecha_desde, fecha_hasta))
        except Exception as e:
            logger.error(f"Error al obtener balance de comprobación: {e}")
            return []