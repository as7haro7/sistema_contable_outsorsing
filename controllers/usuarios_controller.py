from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.usuario_model import UsuarioModel
from models.perfil_model import PerfilModel
from utils.decorators import login_required, permission_required

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios')
@login_required
@permission_required('ADMIN')
def listar():
    usuarios = UsuarioModel.listar()
    return render_template('usuarios/index.html', usuarios=usuarios)

@usuarios_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@permission_required('ADMIN')
def crear():
    empresas = UsuarioModel.empresas_disponibles()
    perfiles = PerfilModel.listar()  # Debes implementar este método
    if request.method == 'POST':
        data = request.form.to_dict()
        data['empresas'] = request.form.getlist('empresas')
        user_id = UsuarioModel.crear(data)
        if user_id:
            # Insertar permisos
            asignado_por = session.get('user_id')
            try:
                asignado_por = int(asignado_por)
            except (TypeError, ValueError):
                asignado_por = None  # O maneja el error como prefieras

            UsuarioModel.asignar_permisos_usuario(user_id, data, asignado_por)
            flash('Usuario creado correctamente', 'success')
            return redirect(url_for('usuarios.listar'))
        else:
            flash('Error al crear usuario', 'danger')
    return render_template('usuarios/create.html', empresas=empresas, perfiles=perfiles)

@usuarios_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('ADMIN')
def editar(id):
    usuario = UsuarioModel.obtener(id)
    empresas = UsuarioModel.empresas_disponibles()
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios.listar'))
    if request.method == 'POST':
        data = request.form.to_dict()
        data['empresas'] = request.form.getlist('empresas')
        UsuarioModel.actualizar(id, data)
        # ACTUALIZA LOS PERMISOS Y PERFIL:
        # Antes de llamar a la función, fuerza el id a entero:
        asignado_por = session.get('user_id')
        try:
            asignado_por = int(asignado_por)
        except (TypeError, ValueError):
            asignado_por = None  # O maneja el error como prefieras

        UsuarioModel.actualizar_permisos_usuario(id, data, asignado_por)
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('usuarios.listar'))
    # Obtener empresas asignadas
    empresas_asignadas = [e['id'] for e in UsuarioModel.get_user_companies(usuario['username'])]
    perfiles = PerfilModel.listar()
    perfil_id_actual = UsuarioModel.get_perfil_id_usuario(id)
    permisos_usuario = UsuarioModel.get_permisos_usuario(id)  # <-- Debes implementar este método

    return render_template(
        'usuarios/edit.html',
        usuario=usuario,
        empresas=empresas,
        empresas_asignadas=empresas_asignadas,
        perfiles=perfiles,
        perfil_id_actual=perfil_id_actual,
        permisos_usuario=permisos_usuario
    )

@usuarios_bp.route('/usuarios/eliminar/<int:id>')
@login_required
@permission_required('ADMIN')
def eliminar(id):
    UsuarioModel.eliminar(id)
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('usuarios.listar'))