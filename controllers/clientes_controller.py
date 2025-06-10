from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.cliente_model import ClienteModel
from utils.decorators import login_required, permission_required, empresa_required

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes')
@login_required
@empresa_required
@permission_required('CONTADOR')
def listar():
    # Aquí iría la lógica para obtener los clientes de la empresa activa
    return render_template('terceros/clientes/index.html')

@clientes_bp.route('/clientes/crear', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def crear():
    if request.method == 'POST':
        # Aquí iría la lógica para crear un nuevo cliente
        flash('Cliente creado correctamente', 'success')
        return redirect(url_for('clientes.listar'))
    return render_template('terceros/clientes/create.html')

@clientes_bp.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def editar(id):
    # Aquí iría la lógica para obtener el cliente por su ID
    if request.method == 'POST':
        # Aquí iría la lógica para actualizar el cliente
        flash('Cliente actualizado correctamente', 'success')
        return redirect(url_for('clientes.listar'))
    return render_template('terceros/clientes/edit.html')

@clientes_bp.route('/clientes/eliminar/<int:id>')
@login_required
@empresa_required
@permission_required('CONTADOR')
def eliminar(id):
    # Aquí iría la lógica para eliminar el cliente
    flash('Cliente eliminado correctamente', 'success')
    return redirect(url_for('clientes.listar'))