from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.iva_model import IvaModel
from utils.decorators import login_required, permission_required, empresa_required

iva_bp = Blueprint('iva', __name__)

@iva_bp.route('/iva/compras')
@login_required
@empresa_required
@permission_required('CONTADOR')
def compras():
    # Aquí iría la lógica para obtener el libro de compras para IVA
    return render_template('iva/compras.html')

@iva_bp.route('/iva/ventas')
@login_required
@empresa_required
@permission_required('CONTADOR')
def ventas():
    # Aquí iría la lógica para obtener el libro de ventas para IVA
    return render_template('iva/ventas.html')

@iva_bp.route('/iva/formularios')
@login_required
@empresa_required
@permission_required('CONTADOR')
def formularios():
    # Aquí iría la lógica para generar formularios de impuestos
    return render_template('iva/formularios.html')

@iva_bp.route('/iva/exportar-compras')
@login_required
@empresa_required
@permission_required('CONTADOR')
def exportar_compras():
    # Aquí iría la lógica para exportar el libro de compras
    flash('Libro de compras exportado correctamente', 'success')
    return redirect(url_for('iva.compras'))

@iva_bp.route('/iva/exportar-ventas')
@login_required
@empresa_required
@permission_required('CONTADOR')
def exportar_ventas():
    # Aquí iría la lógica para exportar el libro de ventas
    flash('Libro de ventas exportado correctamente', 'success')
    return redirect(url_for('iva.ventas'))