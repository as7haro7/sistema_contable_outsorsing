from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.decorators import login_required, permission_required, empresa_required

facturas_bp = Blueprint('facturas', __name__)

@facturas_bp.route('/facturas')
@login_required
@empresa_required
@permission_required('CONTADOR')
def listar():
    # Aquí iría la lógica para obtener todas las facturas de la empresa activa
    return render_template('contabilidad/facturas/index.html')

@facturas_bp.route('/facturas/crear', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def crear():
    if request.method == 'POST':
        # Aquí iría la lógica para crear una nueva factura
        flash('Factura creada correctamente', 'success')
        return redirect(url_for('facturas.listar'))
    return render_template('contabilidad/facturas/create.html')

@facturas_bp.route('/facturas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def editar(id):
    # Aquí iría la lógica para obtener la factura por su ID
    if request.method == 'POST':
        # Aquí iría la lógica para actualizar la factura
        flash('Factura actualizada correctamente', 'success')
        return redirect(url_for('facturas.listar'))
    return render_template('contabilidad/facturas/edit.html')

@facturas_bp.route('/facturas/ver/<int:id>')
@login_required
@empresa_required
@permission_required('CONTADOR')
def ver(id):
    # Aquí iría la lógica para obtener la factura por su ID
    return render_template('contabilidad/facturas/view.html')

@facturas_bp.route('/facturas/anular/<int:id>')
@login_required
@empresa_required
@permission_required('CONTADOR')
def anular(id):
    # Aquí iría la lógica para anular la factura
    flash('Factura anulada correctamente', 'success')
    return redirect(url_for('facturas.listar'))

@facturas_bp.route('/facturas/imprimir/<int:id>')
@login_required
@empresa_required
@permission_required('CONTADOR')
def imprimir(id):
    # Aquí iría la lógica para generar el PDF de la factura
    return render_template('contabilidad/facturas/print.html')

@facturas_bp.route('/facturas/cliente')
@login_required
@empresa_required
@permission_required('CLIENTE')
def cliente_facturas():
    # Aquí iría la lógica para obtener las facturas del cliente
    return render_template('cliente/facturas/index.html')

@facturas_bp.route('/facturas/cliente/ver/<int:id>')
@login_required
@empresa_required
@permission_required('CLIENTE')
def cliente_ver(id):
    # Aquí iría la lógica para obtener la factura por su ID para el cliente
    return render_template('cliente/facturas/view.html')

@facturas_bp.route('/facturas/cliente/descargar/<int:id>')
@login_required
@empresa_required
@permission_required('CLIENTE')
def cliente_descargar(id):
    # Aquí iría la lógica para descargar la factura en PDF
    return redirect(url_for('facturas.cliente_facturas'))