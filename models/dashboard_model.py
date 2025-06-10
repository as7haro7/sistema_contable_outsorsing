from flask import session
from models.database import db_manager

class DashboardContadorModel:
    @staticmethod
    def resumen_dashboard():
        conn = db_manager.get_company_connection(session['empresa_id'])
        # Total compras y ventas
        compras = db_manager.execute_query(conn, "SELECT COUNT(*) as total, COALESCE(SUM(importe),0) as monto FROM LibroCompras WHERE estado != 'ANULADO'")
        ventas = db_manager.execute_query(conn, "SELECT COUNT(*) as total, COALESCE(SUM(importe),0) as monto FROM LibroVentas WHERE estado != 'ANULADO'")
        # Top clientes y proveedores
        top_clientes = db_manager.execute_query(conn, """
            SELECT razonsocial, SUM(importe) as monto FROM LibroVentas
            WHERE estado != 'ANULADO'
            GROUP BY razonsocial ORDER BY monto DESC LIMIT 5
        """)
        top_proveedores = db_manager.execute_query(conn, """
            SELECT p.razon, SUM(lc.importe) as monto FROM LibroCompras lc
            JOIN proveedor p ON lc.proveedor = p.id
            WHERE lc.estado != 'ANULADO'
            GROUP BY p.razon ORDER BY monto DESC LIMIT 5
        """)
        # Ventas y compras por mes (últimos 6 meses)
        ventas_mes = db_manager.execute_query(conn, """
            SELECT TO_CHAR(fecha, 'YYYY-MM') as mes, SUM(importe) as monto
            FROM LibroVentas WHERE estado != 'ANULADO'
            GROUP BY mes ORDER BY mes DESC LIMIT 6
        """)
        compras_mes = db_manager.execute_query(conn, """
            SELECT TO_CHAR(fecha, 'YYYY-MM') as mes, SUM(importe) as monto
            FROM LibroCompras WHERE estado != 'ANULADO'
            GROUP BY mes ORDER BY mes DESC LIMIT 6
        """)
        return {
            'compras': compras[0] if compras else {},
            'ventas': ventas[0] if ventas else {},
            'top_clientes': top_clientes,
            'top_proveedores': top_proveedores,
            'ventas_mes': ventas_mes,
            'compras_mes': compras_mes
        }