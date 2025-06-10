from flask import session
from models.database import db_manager

class FacturaModel:
    """
    Modelo para gestión de facturas de compras y ventas.
    Toda la lógica de validación y cálculo está en PostgreSQL.
    """

    @staticmethod
    def registrar_compra(data):
        """
        Registra una factura de compra usando el procedimiento almacenado.
        Args:
            data (dict): Datos de la factura.
        Returns:
            dict: Resultado con success, message, id y valores calculados.
        """
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = """
                SELECT * FROM sp_registrar_compra(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            params = (
                data['fecha'],                        # p_fecha
                data['nit'],                          # p_nit
                data['proveedor'],                    # p_proveedor
                data['factura'],                      # p_factura
                float(data['importe']),               # p_importe
                data.get('autorizacion'),             # p_autorizacion
                data.get('codigocontrol'),            # p_codigocontrol
                float(data.get('exento', 0)),         # p_exento
                float(data.get('ice', 0)),            # p_ice
                float(data.get('flete', 0)),          # p_flete
                data.get('tipo_fac', 'FACTURA'),      # p_tipo_fac
                session.get('user_nombre', 'sistema') # p_usuario
            )
            result = db_manager.execute_query(conn, query, params)
            if result and len(result) > 0:
                row = result[0]
                return {
                    'success': row['success'],
                    'message': row['message'],
                    'id': row['factura_id'],
                    'valores_calculados': row['valores_calculados']
                }
            else:
                return {'success': False, 'message': 'Error al ejecutar el procedimiento almacenado'}
        except Exception as e:
            return {'success': False, 'message': f'Error del sistema: {str(e)}'}

    @staticmethod
    def registrar_venta(data):
        """
        Registra una factura de venta usando el procedimiento almacenado.
        Args:
            data (dict): Datos de la factura.
        Returns:
            dict: Resultado con success, message, id y valores calculados.
        """
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = """
                SELECT * FROM sp_registrar_venta(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            params = (
                data['fecha'],
                data['nit'],
                data['cliente'],
                data['razonsocial'],
                data['factura'],
                data['autorizacion'],
                data['importe'],
                data.get('exento', 0),
                data.get('ice', 0),
                session.get('user_nombre', 'sistema')
            )
            result = db_manager.execute_query(conn, query, params)
            if result and len(result) > 0:
                row = result[0]
                return {
                    'success': row['success'],
                    'message': row['message'],
                    'id': row['factura_id'],
                    'valores_calculados': row['valores_calculados']
                }
            else:
                return {'success': False, 'message': 'Error al ejecutar el procedimiento almacenado'}
        except Exception as e:
            return {'success': False, 'message': f'Error del sistema: {str(e)}'}

    @staticmethod
    def validar_factura_compra(data):
        """
        Valida los datos de una factura de compra antes del registro.
        """
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            # Validar fecha
            fecha_query = "SELECT validar_fecha_factura(%s::date) as resultado"
            fecha_result = db_manager.execute_query(conn, fecha_query, (data['fecha'],))
            if fecha_result and fecha_result[0]['resultado'] != 'OK':
                return {'success': False, 'message': fecha_result[0]['resultado']}
            # Validar duplicados
            duplicado_query = "SELECT existe_compra_duplicada(%s, %s, %s, %s) as existe"
            duplicado_params = (data['nit'], data['factura'], data['fecha'], data['proveedor'])
            duplicado_result = db_manager.execute_query(conn, duplicado_query, duplicado_params)
            if duplicado_result and duplicado_result[0]['existe']:
                return {'success': False, 'message': 'Ya existe una compra con esos datos'}
            # Calcular valores para mostrar preview
            valores = FacturaModel.calcular_valores_factura(
                data['importe'], data.get('exento', 0), data.get('ice', 0)
            )
            if valores['success']:
                return {'success': True, 'message': 'Validación exitosa', 'valores_calculados': valores}
            else:
                return valores
        except Exception as e:
            return {'success': False, 'message': f'Error del sistema: {str(e)}'}

    @staticmethod
    def validar_factura_venta(data):
        """
        Valida los datos de una factura de venta antes del registro.
        """
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            # Validar fecha
            fecha_query = "SELECT validar_fecha_factura(%s::date) as resultado"
            fecha_result = db_manager.execute_query(conn, fecha_query, (data['fecha'],))
            if fecha_result and fecha_result[0]['resultado'] != 'OK':
                return {'success': False, 'message': fecha_result[0]['resultado']}
            # Validar duplicados
            duplicado_query = "SELECT existe_venta_duplicada(%s, %s, %s, %s) as existe"
            duplicado_params = (data['nit'], data['factura'], data['fecha'], data['cliente'])
            duplicado_result = db_manager.execute_query(conn, duplicado_query, duplicado_params)
            if duplicado_result and duplicado_result[0]['existe']:
                return {'success': False, 'message': 'Ya existe una venta con esos datos'}
            # Calcular valores para mostrar preview
            valores = FacturaModel.calcular_valores_factura(
                data['importe'], data.get('exento', 0), data.get('ice', 0)
            )
            if valores['success']:
                return {'success': True, 'message': 'Validación exitosa', 'valores_calculados': valores}
            else:
                return valores
        except Exception as e:
            return {'success': False, 'message': f'Error del sistema: {str(e)}'}

    @staticmethod
    def calcular_valores_factura(importe, exento=0, ice=0, tasa_iva=0.13):
        """
        Calcula los valores de una factura (neto, IVA, etc.) usando la función de PostgreSQL.
        """
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = "SELECT * FROM calcular_valores_factura(%s, %s, %s, %s)"
            params = (importe, exento, ice, tasa_iva)
            result = db_manager.execute_query(conn, query, params)
            if result and len(result) > 0:
                row = result[0]
                return {
                    'success': True,
                    'neto': float(row['neto']),
                    'iva': float(row['iva']),
                    'total': float(row['total_calculado'])
                }
            else:
                return {'success': False, 'message': 'Error al calcular valores'}
        except Exception as e:
            return {'success': False, 'message': f'Error del sistema: {str(e)}'}

    @staticmethod
    def anular_compra(factura_id, motivo="Anulación manual"):
        """
        Anula una factura de compra.
        """
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = "SELECT * FROM sp_anular_compra(%s, %s, %s)"
            params = (factura_id, motivo, session.get('user_nombre', 'sistema'))
            result = db_manager.execute_query(conn, query, params)
            if result and len(result) > 0:
                row = result[0]
                return {'success': row['success'], 'message': row['message']}
            else:
                return {'success': False, 'message': 'Error al ejecutar el procedimiento almacenado'}
        except Exception as e:
            return {'success': False, 'message': f'Error del sistema: {str(e)}'}

    @staticmethod
    def anular_venta(factura_id, motivo="Anulación manual"):
        """
        Anula una factura de venta.
        """
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = "SELECT * FROM sp_anular_venta(%s, %s, %s)"
            params = (factura_id, motivo, session.get('user_nombre', 'sistema'))
            result = db_manager.execute_query(conn, query, params)
            if result and len(result) > 0:
                row = result[0]
                return {'success': row['success'], 'message': row['message']}
            else:
                return {'success': False, 'message': 'Error al ejecutar el procedimiento almacenado'}
        except Exception as e:
            return {'success': False, 'message': f'Error del sistema: {str(e)}'}

    @staticmethod
    def listar_compras():
        """Devuelve todas las compras registradas."""
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = "SELECT * FROM LibroCompras ORDER BY fecha DESC, id DESC"
            return db_manager.execute_query(conn, query)
        except Exception as e:
            return []

    @staticmethod
    def listar_ventas():
        """Devuelve todas las ventas registradas."""
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = "SELECT * FROM LibroVentas ORDER BY fecha DESC, id DESC"
            return db_manager.execute_query(conn, query)
        except Exception as e:
            return []

    @staticmethod
    def obtener_compra(factura_id):
        """Devuelve el detalle de una compra."""
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = "SELECT * FROM LibroCompras WHERE id = %s"
            result = db_manager.execute_query(conn, query, (factura_id,))
            return result[0] if result else None
        except Exception as e:
            return None

    @staticmethod
    def obtener_venta(factura_id):
        """Devuelve el detalle de una venta."""
        try:
            conn = db_manager.get_company_connection(session['empresa_id'])
            query = "SELECT * FROM LibroVentas WHERE id = %s"
            result = db_manager.execute_query(conn, query, (factura_id,))
            return result[0] if result else None
        except Exception as e:
            return None

    # Métodos de consulta y reportes (resúmenes, detalles, auditoría) pueden mantenerse igual,
    # ya que son útiles para la gestión y no generan duplicidad ni lógica innecesaria.