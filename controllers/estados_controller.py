from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.estado_model import EstadoModel
from utils.decorators import login_required, permission_required, empresa_required

estados_bp = Blueprint('estados', __name__)

@estados_bp.route('/estados/balance-general')
@login_required
@empresa_required
@permission_required('CONTADOR')
def balance_general():
    # Aquí iría la lógica para obtener el balance general de la empresa activa
    return render_template('contabilidad/estados/balance_general.html')

@estados_bp.route('/estados/estado-resultados')
@login_required
@empresa_required
@permission_required('CONTADOR')
def estado_resultados():
    # Aquí iría la lógica para obtener el estado de resultados de la empresa activa
    return render_template('contabilidad/estados/estado_resultados.html')

@estados_bp.route('/estados/flujo-efectivo')
@login_required
@empresa_required
@permission_required('CONTADOR')
def flujo_efectivo():
    # Aquí iría la lógica para obtener el flujo de efectivo de la empresa activa
    return render_template('contabilidad/estados/flujo_efectivo.html')

@estados_bp.route('/estados/cambios-patrimonio')
@login_required
@empresa_required
@permission_required('CONTADOR')
def cambios_patrimonio():
    # Aquí iría la lógica para obtener el estado de cambios en el patrimonio
    return render_template('contabilidad/estados/cambios_patrimonio.html')