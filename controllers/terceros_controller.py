from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.tercero_model import TerceroModel
from utils.decorators import login_required, empresa_required

terceros_bp = Blueprint('terceros', __name__, url_prefix='/terceros')

@terceros_bp.route('/')
@login_required
@empresa_required
def index():
    """Lista todos los terceros (clientes y proveedores)"""
    tipo = request.args.get('tipo')  # 'cliente', 'proveedor' o None
    terceros = TerceroModel.get_all(tipo)
    return render_template('terceros/index.html', terceros=terceros, tipo=tipo)

@terceros_bp.route('/ver/<tipo>/<int:tercero_id>')
@login_required
@empresa_required
def ver(tipo, tercero_id):
    """Ver detalle de un tercero"""
    tercero = TerceroModel.get_by_id(tercero_id, tipo)
    contactos = TerceroModel.get_contactos(tercero_id, tipo)
    if not tercero:
        flash('Tercero no encontrado', 'danger')
        return redirect(url_for('terceros.index'))
    return render_template('terceros/detalle.html', tercero=tercero, contactos=contactos, tipo=tipo)

@terceros_bp.route('/crear/<tipo>', methods=['GET', 'POST'])
@login_required
@empresa_required
def crear(tipo):
    """Crear un nuevo tercero"""
    if request.method == 'POST':
        data = request.form.to_dict()
        tercero_id = TerceroModel.create(data, tipo)
        if tercero_id:
            flash('Tercero creado correctamente', 'success')
            return redirect(url_for('terceros.ver', tipo=tipo, tercero_id=tercero_id))
        else:
            flash('Error al crear tercero', 'danger')
    return render_template('terceros/create.html', tipo=tipo)

@terceros_bp.route('/editar/<tipo>/<int:tercero_id>', methods=['GET', 'POST'])
@login_required
@empresa_required
def editar(tipo, tercero_id):
    """Editar un tercero existente"""
    tercero = TerceroModel.get_by_id(tercero_id, tipo)
    if not tercero:
        flash('Tercero no encontrado', 'danger')
        return redirect(url_for('terceros.index'))
    if request.method == 'POST':
        data = request.form.to_dict()
        ok = TerceroModel.update(tercero_id, data, tipo)
        if ok:
            flash('Tercero actualizado', 'success')
            return redirect(url_for('terceros.ver', tipo=tipo, tercero_id=tercero_id))
        else:
            flash('Error al actualizar tercero', 'danger')
    return render_template('terceros/edit.html', tercero=tercero, tipo=tipo)

@terceros_bp.route('/eliminar/<tipo>/<int:tercero_id>', methods=['POST'])
@login_required
@empresa_required
def eliminar(tipo, tercero_id):
    """Eliminar un tercero (borrado lógico o físico según modelo)"""
    ok = TerceroModel.delete(tercero_id, tipo)
    if ok:
        flash('Tercero eliminado', 'success')
    else:
        flash('Error al eliminar tercero', 'danger')
    return redirect(url_for('terceros.index'))

@terceros_bp.route('/contactos/<tipo>/<int:tercero_id>/agregar', methods=['POST'])
@login_required
@empresa_required
def agregar_contacto(tipo, tercero_id):
    """Agregar contacto a un tercero"""
    data = request.form.to_dict()
    ok = TerceroModel.add_contacto(tercero_id, data, tipo)
    if ok:
        flash('Contacto agregado', 'success')
    else:
        flash('Error al agregar contacto', 'danger')
    return redirect(url_for('terceros.ver', tipo=tipo, tercero_id=tercero_id))