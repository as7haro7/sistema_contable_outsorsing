from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.empresa_model import EmpresaModel
from utils.decorators import login_required, permission_required

empresas_bp = Blueprint('empresas', __name__)

@empresas_bp.route('/empresas')
@login_required
@permission_required('ADMIN')
def listar():
    # Paginación y búsqueda
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page
    termino = request.args.get('q', '').strip()
    activo = request.args.get('activo')
    empresas = []
    total = 0

    if termino:
        empresas = EmpresaModel.buscar_empresas(termino)
        total = len(empresas)
    else:
        empresas = EmpresaModel.listar_empresas(activo=activo if activo in ['true', 'false'] else None, limit=per_page, offset=offset)
        # Para paginación real, deberías tener un método que devuelva el total de empresas
        total = len(EmpresaModel.listar_empresas(activo=activo if activo in ['true', 'false'] else None))

    estadisticas = EmpresaModel.obtener_estadisticas_empresa()
    return render_template('empresas/index.html',
                           empresas=empresas,
                           page=page,
                           per_page=per_page,
                           total=total,
                           termino=termino,
                           estadisticas=estadisticas)

@empresas_bp.route('/empresas/crear', methods=['GET', 'POST'])
@login_required
@permission_required('ADMIN')
def crear():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['usuario_creacion'] = session.get('user_nombre', 'SYSTEM')
        # Validar NIT único
        if not EmpresaModel.validar_nit_unico(data['nit']):
            flash('El NIT ya está registrado en otra empresa.', 'danger')
            return render_template('empresas/create.html', data=data)
        resultado = EmpresaModel.crear_empresa(data)
        if resultado.get('success'):
            flash('Empresa creada correctamente', 'success')
            return redirect(url_for('empresas.listar'))
        else:
            flash(resultado.get('message', 'Error al crear empresa'), 'danger')
    return render_template('empresas/create.html')

@empresas_bp.route('/empresas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('ADMIN')
def editar(id):
    empresa = EmpresaModel.obtener_empresa_por_id(id)
    if not empresa:
        flash('Empresa no encontrada', 'warning')
        return redirect(url_for('empresas.listar'))
    if request.method == 'POST':
        data = request.form.to_dict()
        data['usuario_actualizacion'] = session.get('user_nombre', 'SYSTEM')
        # Validar NIT único (excluyendo la empresa actual)
        if not EmpresaModel.validar_nit_unico(data['nit'], empresa_id=id):
            flash('El NIT ya está registrado en otra empresa.', 'danger')
            return render_template('empresas/edit.html', empresa=empresa)
        resultado = EmpresaModel.actualizar_empresa(id, data)
        if resultado.get('success'):
            flash('Empresa actualizada correctamente', 'success')
            return redirect(url_for('empresas.listar'))
        else:
            flash(resultado.get('message', 'Error al actualizar empresa'), 'danger')
    return render_template('empresas/edit.html', empresa=empresa)

@empresas_bp.route('/empresas/eliminar/<int:id>')
@login_required
@permission_required('ADMIN')
def eliminar(id):
    resultado = EmpresaModel.eliminar_empresa(id, usuario_eliminacion=session.get('user_nombre', 'SYSTEM'))
    if resultado.get('success'):
        flash('Empresa desactivada correctamente', 'success')
    else:
        flash(resultado.get('message', 'Error al desactivar empresa'), 'danger')
    return redirect(url_for('empresas.listar'))

@empresas_bp.route('/empresas/eliminar_definitivo/<int:id>')
@login_required
@permission_required('ADMIN')
def eliminar_definitivo(id):
    resultado = EmpresaModel.eliminar_empresa_definitivo(id)
    if resultado.get('success'):
        flash('Empresa eliminada definitivamente', 'success')
    else:
        flash(resultado.get('message', 'Error al eliminar empresa'), 'danger')
    return redirect(url_for('empresas.listar'))

@empresas_bp.route('/empresas/estructura/<int:id>', methods=['POST'])
@login_required
@permission_required('ADMIN')
def crear_estructura_contable(id):
    empresa = EmpresaModel.obtener_empresa_por_id(id)
    if not empresa:
        flash('Empresa no encontrada', 'warning')
        return redirect(url_for('empresas.listar'))
    try:
        EmpresaModel.crear_estructura_contable(empresa['id'])
        flash('Estructura contable creada/recreada correctamente.', 'success')
    except Exception as e:
        flash(f'Error al crear estructura contable: {str(e)}', 'danger')
    return redirect(url_for('empresas.listar'))

@empresas_bp.route('/empresas/buscar', methods=['GET'])
@login_required
@permission_required('ADMIN')
def buscar():
    termino = request.args.get('q', '').strip()
    empresas = EmpresaModel.buscar_empresas(termino) if termino else []
    return render_template('empresas/index.html', empresas=empresas, termino=termino)

@empresas_bp.route('/empresas/activar/<int:id>')
@login_required
@permission_required('ADMIN')
def activar(id):
    resultado = EmpresaModel.activar_empresa(id, usuario_activacion=session.get('user_nombre', 'SYSTEM'))
    if resultado.get('success'):
        flash('Empresa reactivada correctamente', 'success')
    else:
        flash(resultado.get('message', 'Error al reactivar empresa'), 'danger')
    return redirect(url_for('empresas.listar'))

@empresas_bp.route('/empresas/backup/<int:id>')
@login_required
@permission_required('ADMIN')
def backup_contabilidad(id):
    resultado = EmpresaModel.backup_contabilidad(id)
    if resultado.get('success'):
        flash(resultado['message'], 'success')
    else:
        flash(resultado['message'], 'danger')
    return redirect(url_for('empresas.listar'))