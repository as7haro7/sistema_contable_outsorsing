from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.proveedor_model import ProveedorModel
from utils.decorators import login_required, permission_required, empresa_required

proveedores_bp = Blueprint('proveedores', __name__)

@proveedores_bp.route('/proveedores')
@login_required
@empresa_required
@permission_required('CONTADOR')
def listar():
    # Aquí iría la lógica para obtener los proveedores de la empresa activa
    return render_template('terceros/proveedores/index.html')

@proveedores_bp.route('/proveedores/crear', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def crear():
    if request.method == 'POST':
        # Aquí iría la lógica para crear un nuevo proveedor
        flash('Proveedor creado correctamente', 'success')
        return redirect(url_for('proveedores.listar'))
    return render_template('terceros/proveedores/create.html')

@proveedores_bp.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def editar(id):
    # Aquí iría la lógica para obtener el proveedor por su ID
    if request.method == 'POST':
        # Aquí iría la lógica para actualizar el proveedor
        flash('Proveedor actualizado correctamente', 'success')
        return redirect(url_for('proveedores.listar'))
    return render_template('terceros/proveedores/edit.html')

@proveedores_bp.route('/proveedores/eliminar/<int:id>')
@login_required
@empresa_required
@permission_required('CONTADOR')
def eliminar(id):
    # Aquí iría la lógica para eliminar el proveedor
    flash('Proveedor eliminado correctamente', 'success')
    return redirect(url_for('proveedores.listar'))