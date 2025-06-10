from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.decorators import login_required, permission_required, empresa_required

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/cliente/dashboard')
@login_required
@empresa_required
@permission_required('CLIENTE')
def dashboard():
    # Aquí iría la lógica para mostrar el dashboard del cliente
    return render_template('cliente_portal/dashboard.html')

@cliente_bp.route('/cliente/estados-financieros')
@login_required
@empresa_required
@permission_required('CLIENTE')
def estados_financieros():
    # Aquí iría la lógica para mostrar los estados financieros al cliente
    return render_template('cliente_portal/estados_financieros.html')

@cliente_bp.route('/cliente/reportes')
@login_required
@empresa_required
@permission_required('CLIENTE')
def reportes():
    # Aquí iría la lógica para mostrar los reportes al cliente
    return render_template('cliente_portal/reportes.html')

@cliente_bp.route('/cliente/facturas')
@login_required
@empresa_required
@permission_required('CLIENTE')
def facturas():
    # Aquí iría la lógica para mostrar las facturas al cliente
    return render_template('cliente_portal/facturas.html')

@cliente_bp.route('/cliente/descargas')
@login_required
@empresa_required
@permission_required('CLIENTE')
def descargas():
    # Aquí iría la lógica para mostrar las descargas disponibles al cliente
    return render_template('cliente_portal/descargas.html')