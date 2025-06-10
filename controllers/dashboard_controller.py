from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.dashboard_model import DashboardContadorModel

from models.empresa_model import EmpresaModel
from models.usuario_model import UsuarioModel
from models.gestion_model import GestionModel

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def index():
    permissions = session.get('permissions', {})
    print(permissions)
    if 'ADMIN' in permissions:
        # Estadísticas para admin
        estadisticas = EmpresaModel.obtener_estadisticas_empresa()
        total_usuarios = len(UsuarioModel.listar())
        total_gestiones = 0
        try:
            from models.database import db_manager
            conn = db_manager.get_master_connection()
            result = db_manager.execute_query(conn, "SELECT COUNT(*) as total FROM gestiones")
            total_gestiones = result[0]['total'] if result else 0
        except:
            pass
        return render_template('dashboard/admin.html',
                               estadisticas=estadisticas,
                               total_usuarios=total_usuarios,
                               total_gestiones=total_gestiones)
    elif 'CONTADOR' in permissions:
        data = DashboardContadorModel.resumen_dashboard()
        return render_template('dashboard/contador.html', data=data)
    # elif 'CLIENTE' in permissions:
    elif 'CONSULTOR' in permissions:
        return render_template('dashboard/cliente.html')
    else:
        return "<h1>No tienes un dashboard asignado</h1>"      
    

@dashboard_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))