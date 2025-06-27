from models.database import db_manager
import logging

logger = logging.getLogger(__name__)

class PlancuentaModel:

    @staticmethod
    def obtener_todas_cuentas(empresa_id):
        """Obtiene todas las cuentas del plan contable"""
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT p.*, 
                       tc.descrip AS tipo_cuenta_descrip,
                       m.descrip AS moneda_descrip,
                       mv.descrip AS tipomov_descrip,
                       calcular_saldo_cuenta(p.cuenta) AS saldo
                FROM Plancuenta p
                LEFT JOIN TipoCuenta tc ON p.tipo_cuenta = tc.codigo
                LEFT JOIN Moneda m ON p.moneda = m.codigo
                LEFT JOIN MovCuenta mv ON p.tipomov = mv.codigo
                ORDER BY p.cuenta
            """
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener cuentas: {e}")
            return []

    @staticmethod
    def obtener_arbol_cuentas(empresa_id):
        """Devuelve las cuentas en estructura de árbol"""
        try:
            cuentas = PlancuentaModel.obtener_todas_cuentas(empresa_id)
            arbol = []
            cuentas_dict = {c['cuenta']: dict(c, hijos=[]) for c in cuentas}
            for cuenta in cuentas:
                partes = cuenta['cuenta'].split('.')
                if len(partes) == 1:
                    arbol.append(cuentas_dict[cuenta['cuenta']])
                else:
                    padre = '.'.join(partes[:-1])
                    if padre in cuentas_dict:
                        cuentas_dict[padre]['hijos'].append(cuentas_dict[cuenta['cuenta']])
            return arbol
        except Exception as e:
            logger.error(f"Error al construir árbol: {e}")
            return []

    @staticmethod
    def obtener_cuenta_por_codigo(empresa_id, codigo):
        try:
            logger.info(f"Buscando cuenta con código: {codigo}")
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                SELECT p.*, 
                    tc.descrip AS tipo_cuenta_descrip,
                    m.descrip AS moneda_descrip,
                    mv.descrip AS tipomov_descrip,
                    calcular_saldo_cuenta(p.cuenta) AS saldo
                FROM Plancuenta p
                LEFT JOIN TipoCuenta tc ON p.tipo_cuenta = tc.codigo
                LEFT JOIN Moneda m ON p.moneda = m.codigo
                LEFT JOIN MovCuenta mv ON p.tipomov = mv.codigo
                WHERE p.cuenta = %s;
            """
            result = db_manager.execute_query(conn, query, (codigo,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error al obtener cuenta {codigo}: {e}")
            return None

    @staticmethod
    def crear_cuenta(empresa_id, datos, usuario):
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                INSERT INTO Plancuenta (cuenta, tipo_cuenta, nivel, descrip, tipomov, moneda, fecha, usuario, fechasys)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE, %s, NOW())
            """
            params = (
                datos['cuenta'], datos['tipo_cuenta'], datos['nivel'], datos['descrip'],
                datos['tipomov'], datos['moneda'], usuario
            )
            db_manager.execute_query(conn, query, params, fetch=False)
            return {'success': True, 'message': 'Cuenta creada correctamente'}
        except Exception as e:
            logger.error(f"Error al crear cuenta: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def actualizar_cuenta(empresa_id, codigo, datos, usuario):
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = """
                UPDATE Plancuenta
                SET descrip=%s, tipo_cuenta=%s, nivel=%s, tipomov=%s, moneda=%s, usuario=%s, fechasys=NOW()
                WHERE cuenta=%s
            """
            params = (
                datos['descrip'], datos['tipo_cuenta'], datos['nivel'],
                datos['tipomov'], datos['moneda'], usuario, codigo
            )
            db_manager.execute_query(conn, query, params, fetch=False)
            return {'success': True, 'message': 'Cuenta actualizada correctamente'}
        except Exception as e:
            logger.error(f"Error al actualizar cuenta: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def eliminar_cuenta(empresa_id, codigo):
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "DELETE FROM Plancuenta WHERE cuenta=%s"
            db_manager.execute_query(conn, query, (codigo,), fetch=False)
            return {'success': True, 'message': 'Cuenta eliminada correctamente'}
        except Exception as e:
            logger.error(f"Error al eliminar cuenta: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def obtener_niveles(empresa_id):
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT nivel, digitos FROM Nivel ORDER BY nivel"
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener niveles: {e}")
            return []

    @staticmethod
    def obtener_tipos_cuenta(empresa_id):
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT codigo, descrip FROM TipoCuenta ORDER BY codigo"
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener tipos de cuenta: {e}")
            return []

    @staticmethod
    def obtener_tipos_movimiento(empresa_id):
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT codigo, descrip FROM MovCuenta ORDER BY codigo"
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener tipos de movimiento: {e}")
            return []

    @staticmethod
    def obtener_monedas(empresa_id):
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT codigo, descrip FROM Moneda ORDER BY codigo"
            return db_manager.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Error al obtener monedas: {e}")
            return []

    @staticmethod
    def tiene_movimientos(empresa_id, codigo):
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT 1 FROM Asiento_det WHERE cuenta=%s LIMIT 1"
            result = db_manager.execute_query(conn, query, (codigo,))
            return bool(result)
        except Exception as e:
            logger.error(f"Error al verificar movimientos: {e}")
            return False

    @staticmethod
    def validar_estructura_cuenta(cuenta):
        # Ejemplo simple: no permitir cuentas vacías ni duplicadas
        if not cuenta or cuenta.strip() == "":
            return False, "El código de cuenta no puede estar vacío"
        # Aquí podrías agregar más validaciones si lo necesitas
        return True, ""