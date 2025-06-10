from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.gestion_model import GestionModel
from utils.decorators import login_required, permission_required

gestiones_bp = Blueprint('gestiones', __name__)

@gestiones_bp.route('/empresas/<int:empresa_id>/gestiones')
@login_required
@permission_required('ADMIN')
def listar(empresa_id):
    gestiones = GestionModel.listar_gestiones(empresa_id)
    return render_template('gestiones/index.html', gestiones=gestiones, empresa_id=empresa_id)

@gestiones_bp.route('/empresas/<int:empresa_id>/gestiones/crear', methods=['GET', 'POST'])
@login_required
@permission_required('ADMIN')
def crear(empresa_id):
    if request.method == 'POST':
        data = request.form.to_dict()
        data['empresa_id'] = empresa_id
        data['usuario_creacion'] = session.get('user_nombre', 'SYSTEM')
        GestionModel.crear_gestion(data)
        flash('Gestión creada correctamente', 'success')
        return redirect(url_for('gestiones.listar', empresa_id=empresa_id))
    return render_template('gestiones/create.html', empresa_id=empresa_id)

@gestiones_bp.route('/gestiones/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('ADMIN')
def editar(id):
    gestion = GestionModel.obtener_gestion(id)
    if not gestion:
        flash('Gestión no encontrada', 'danger')
        return redirect(url_for('empresas.listar'))
    if request.method == 'POST':
        data = request.form.to_dict()
        GestionModel.actualizar_gestion(id, data)
        flash('Gestión actualizada correctamente', 'success')
        return redirect(url_for('gestiones.listar', empresa_id=gestion['empresa_id']))
    return render_template('gestiones/edit.html', gestion=gestion)

@gestiones_bp.route('/gestiones/eliminar/<int:id>')
@login_required
@permission_required('ADMIN')
def eliminar(id):
    gestion = GestionModel.obtener_gestion(id)
    if gestion:
        GestionModel.eliminar_gestion(id)
        flash('Gestión eliminada', 'success')
        return redirect(url_for('gestiones.listar', empresa_id=gestion['empresa_id']))
    flash('Gestión no encontrada', 'danger')
    return redirect(url_for('empresas.listar'))