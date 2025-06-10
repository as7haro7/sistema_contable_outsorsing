from models.database import db_manager
import logging

logger = logging.getLogger(__name__)

class PlancuentaModel:

    @staticmethod
    def obtener_todas_cuentas(empresa_id):
        """
        Obtiene todas las cuentas del plan contable usando una función almacenada.
        La función almacenada debería devolver un CURSOR o un conjunto de resultados.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            # Asumiendo que 'sp_obtener_todas_cuentas' es una función que retorna un REFCURSOR o una tabla
            query = "SELECT * FROM sp_obtener_todas_cuentas(%s)"
            return db_manager.execute_query(conn, query, (empresa_id,))
        except Exception as e:
            logger.error(f"Error al obtener cuentas desde SP: {e}")
            return []

    @staticmethod
    def obtener_arbol_cuentas(empresa_id):
        """
        Devuelve las cuentas en estructura de árbol.
        Esta lógica de construcción del árbol se mantiene en Python,
        ya que es más eficiente aquí después de obtener las cuentas planas.
        Podríamos obtener un árbol pre-construido de la BD si la estructura de la cuenta lo permite
        y la BD tiene funciones recursivas para ello (ej. CTEs recursivas).
        Por simplicidad, mantenemos la construcción en Python.
        """
        try:
            # Reutilizamos la función que ahora llama a un SP
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
        """
        Obtiene una cuenta por su código usando una función almacenada.
        """
        try:
            logger.info(f"Buscando cuenta con código: {codigo} usando SP")
            conn = db_manager.get_company_connection(empresa_id)
            # Asumiendo que 'sp_obtener_cuenta_por_codigo' retorna un registro o NULL
            query = "SELECT * FROM sp_obtener_cuenta_por_codigo(%s, %s)"
            result = db_manager.execute_query(conn, query, (empresa_id, codigo))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error al obtener cuenta {codigo} desde SP: {e}")
            return None

    @staticmethod
    def crear_cuenta(empresa_id, datos, usuario):
        """
        Crea una cuenta usando un procedimiento almacenado.
        'fechasys' y 'usuario' pueden ser manejados por un TRIGGER en la BD.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            # Asumiendo que 'sp_crear_cuenta' es un procedimiento almacenado
            # que toma los parámetros necesarios y maneja la inserción.
            # No se pasa 'fecha' ni 'fechasys' ni 'usuario' si son manejados por TRIGGER.
            # Si el SP los requiere explícitamente, se deberían añadir a params.
            query = "CALL sp_crear_cuenta(%s, %s, %s, %s, %s, %s, %s)"
            params = (
                empresa_id, datos['cuenta'], datos['tipo_cuenta'], datos['nivel'],
                datos['descrip'], datos['tipomov'], datos['moneda']
                # 'usuario' no se pasa si es manejado por trigger,
                # de lo contrario, se agregaría aquí.
            )
            db_manager.execute_query(conn, query, params, fetch=False)
            return {'success': True, 'message': 'Cuenta creada correctamente mediante SP'}
        except Exception as e:
            logger.error(f"Error al crear cuenta mediante SP: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def actualizar_cuenta(empresa_id, codigo, datos, usuario):
        """
        Actualiza una cuenta usando un procedimiento almacenado.
        'fechasys' y 'usuario' pueden ser manejados por un TRIGGER en la BD.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            # Asumiendo que 'sp_actualizar_cuenta' es un procedimiento almacenado
            query = "CALL sp_actualizar_cuenta(%s, %s, %s, %s, %s, %s, %s)"
            params = (
                empresa_id, codigo, datos['descrip'], datos['tipo_cuenta'],
                datos['nivel'], datos['tipomov'], datos['moneda']
                # 'usuario' no se pasa si es manejado por trigger,
                # de lo contrario, se agregaría aquí.
            )
            db_manager.execute_query(conn, query, params, fetch=False)
            return {'success': True, 'message': 'Cuenta actualizada correctamente mediante SP'}
        except Exception as e:
            logger.error(f"Error al actualizar cuenta mediante SP: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def eliminar_cuenta(empresa_id, codigo):
        """
        Elimina una cuenta usando un procedimiento almacenado.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            # Asumiendo que 'sp_eliminar_cuenta' es un procedimiento almacenado
            query = "CALL sp_eliminar_cuenta(%s, %s)"
            db_manager.execute_query(conn, query, (empresa_id, codigo), fetch=False)
            return {'success': True, 'message': 'Cuenta eliminada correctamente mediante SP'}
        except Exception as e:
            logger.error(f"Error al eliminar cuenta mediante SP: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def obtener_niveles(empresa_id):
        """
        Obtiene los niveles usando una función almacenada.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT * FROM sp_obtener_niveles(%s)"
            return db_manager.execute_query(conn, query, (empresa_id,))
        except Exception as e:
            logger.error(f"Error al obtener niveles desde SP: {e}")
            return []

    @staticmethod
    def obtener_tipos_cuenta(empresa_id):
        """
        Obtiene los tipos de cuenta usando una función almacenada.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT * FROM sp_obtener_tipos_cuenta(%s)"
            return db_manager.execute_query(conn, query, (empresa_id,))
        except Exception as e:
            logger.error(f"Error al obtener tipos de cuenta desde SP: {e}")
            return []

    @staticmethod
    def obtener_tipos_movimiento(empresa_id):
        """
        Obtiene los tipos de movimiento usando una función almacenada.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT * FROM sp_obtener_tipos_movimiento(%s)"
            return db_manager.execute_query(conn, query, (empresa_id,))
        except Exception as e:
            logger.error(f"Error al obtener tipos de movimiento desde SP: {e}")
            return []

    @staticmethod
    def obtener_monedas(empresa_id):
        """
        Obtiene las monedas usando una función almacenada.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT * FROM sp_obtener_monedas(%s)"
            return db_manager.execute_query(conn, query, (empresa_id,))
        except Exception as e:
            logger.error(f"Error al obtener monedas desde SP: {e}")
            return []

    @staticmethod
    def tiene_movimientos(empresa_id, codigo):
        """
        Verifica si una cuenta tiene movimientos usando una función almacenada.
        """
        try:
            conn = db_manager.get_company_connection(empresa_id)
            query = "SELECT sp_tiene_movimientos(%s, %s)"
            result = db_manager.execute_query(conn, query, (empresa_id, codigo))
            return bool(result and result[0][0]) # Assuming the function returns boolean or 0/1
        except Exception as e:
            logger.error(f"Error al verificar movimientos desde SP: {e}")
            return False

    @staticmethod
    def validar_estructura_cuenta(cuenta):
        # Esta validación se mantiene en la capa de aplicación, ya que es una validación de formato
        # y no una operación de base de datos.
        if not cuenta or cuenta.strip() == "":
            return False, "El código de cuenta no puede estar vacío"
        return True, ""