from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.decorators import login_required, permission_required, empresa_required

periodos_bp = Blueprint('periodos', __name__)

@periodos_bp.route('/periodos')
@login_required
@empresa_required
@permission_required('CONTADOR')
def gestionar():
    # Aquí iría la lógica para obtener los períodos de la empresa activa
    return render_template('contabilidad/periodos/index.html')

@periodos_bp.route('/periodos/crear', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def crear():
    if request.method == 'POST':
        # Aquí iría la lógica para crear un nuevo período
        flash('Período creado correctamente', 'success')
        return redirect(url_for('periodos.gestionar'))
    return render_template('contabilidad/periodos/create.html')

@periodos_bp.route('/periodos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def editar(id):
    # Aquí iría la lógica para obtener el período por su ID
    if request.method == 'POST':
        # Aquí iría la lógica para actualizar el período
        flash('Período actualizado correctamente', 'success')
        return redirect(url_for('periodos.gestionar'))
    return render_template('contabilidad/periodos/edit.html')

@periodos_bp.route('/periodos/cerrar/<int:id>')
@login_required
@empresa_required
@permission_required('CONTADOR')
def cerrar(id):
    # Aquí iría la lógica para cerrar un período contable
    flash('Período cerrado correctamente', 'success')
    return redirect(url_for('periodos.gestionar'))

@periodos_bp.route('/periodos/reabrir/<int:id>')
@login_required
@empresa_required
@permission_required('CONTADOR')
def reabrir(id):
    # Aquí iría la lógica para reabrir un período contable
    flash('Período reabierto correctamente', 'success')
    return redirect(url_for('periodos.gestionar'))