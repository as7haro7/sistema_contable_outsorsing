from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.reporte_model import ReporteModel
from utils.decorators import login_required, permission_required, empresa_required

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes')
@login_required
@empresa_required
@permission_required('CONTADOR')
def index():
    # Aquí iría la lógica para mostrar la página principal de reportes
    return render_template('reportes/index.html')

@reportes_bp.route('/reportes/balance-general')
@login_required
@empresa_required
@permission_required('CONTADOR')
def balance_general():
    # Aquí iría la lógica para generar el reporte de balance general
    return render_template('reportes/balance_general.html')

@reportes_bp.route('/reportes/estado-resultados')
@login_required
@empresa_required
@permission_required('CONTADOR')
def estado_resultados():
    # Aquí iría la lógica para generar el reporte de estado de resultados
    return render_template('reportes/estado_resultados.html')

@reportes_bp.route('/reportes/libro-diario')
@login_required
@empresa_required
@permission_required('CONTADOR')
def libro_diario():
    # Aquí iría la lógica para generar el reporte de libro diario
    return render_template('reportes/libro_diario.html')

@reportes_bp.route('/reportes/libro-mayor')
@login_required
@empresa_required
@permission_required('CONTADOR')
def libro_mayor():
    # Aquí iría la lógica para generar el reporte de libro mayor
    return render_template('reportes/libro_mayor.html')

@reportes_bp.route('/reportes/libro-compras')
@login_required
@empresa_required
@permission_required('CONTADOR')
def libro_compras():
    # Aquí iría la lógica para generar el reporte de libro de compras
    return render_template('reportes/libro_compras.html')

@reportes_bp.route('/reportes/libro-ventas')
@login_required
@empresa_required
@permission_required('CONTADOR')
def libro_ventas():
    # Aquí iría la lógica para generar el reporte de libro de ventas
    return render_template('reportes/libro_ventas.html')