from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.auth_model import AuthModel
from utils.decorators import logout_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor complete todos los campos', 'error')
            return render_template('auth/login.html')
        
        user = AuthModel.authenticate_user(username, password)
        
        if user:
            # Guardar datos en sesión
            session['user_id'] = user['usuario']
            session['username'] = user['usuario']
            session['user_name'] = user['nombre']
            session['empresa_id'] = user['id_empresa']
            session['empresa_nombre'] = user['empresa_nombre']
            
            # Obtener permisos
            permissions = AuthModel.get_user_permissions(username)
            session['permissions'] = {perm['perfil']: perm for perm in permissions}
            
            return redirect(url_for('auth.select_empresa'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/select-empresa')
def select_empresa():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Obtener empresas del usuario
    empresas = AuthModel.get_user_companies(session['user_id'])
    
    # Si solo tiene una empresa, redirigir directamente
    if len(empresas) == 1:
        session['empresa_id'] = empresas[0]['id']
        session['empresa_nombre'] = empresas[0]['razon']
        return redirect(url_for('auth.select_gestion'))
    
    return render_template('auth/select_empresa.html', empresas=empresas)


# @auth_bp.route('/select-gestion')
# def select_gestion():
#     if 'empresa_id' not in session:
#         return redirect(url_for('auth.select_empresa'))

#     # Obtener gestiones de la empresa
#     gestiones = AuthModel.get_company_gestiones(session['empresa_id'])
#     permissions = session.get('permissions', {})

#     # Si es ADMIN, va directo al dashboard
#     if 'ADMIN' in permissions:
#         return redirect(url_for('dashboard.index'))

#     # Si es CLIENTE y solo tiene una gestión, la selecciona automáticamente
#     if 'CLIENTE' in permissions and len(gestiones) == 1:
#         gestion_actual = gestiones[0]
#         session['gestion_id'] = gestion_actual['id']
#         session['gestion_nombre'] = gestion_actual['descrip']
#         session['gestion_year'] = gestion_actual['gestion']
#         session['moneda_base'] = gestion_actual['moneda']
#         return redirect(url_for('dashboard.index'))

#     # Si es CONTADOR o cualquier otro, muestra el selector
#     return render_template('auth/select_empresa.html', gestiones=gestiones)
@auth_bp.route('/select-gestion', methods=['GET', 'POST'])
def select_gestion():
    if 'empresa_id' not in session:
        return redirect(url_for('auth.select_empresa'))

    gestiones = AuthModel.get_company_gestiones(session['empresa_id'])
    session['gestiones_disponibles'] = gestiones

    permissions = session.get('permissions', {})

    # ADMIN va directo al dashboard
    if 'ADMIN' in permissions:
        return redirect(url_for('dashboard.index'))

    # CLIENTE con una sola gestión, la selecciona automáticamente
    if 'CLIENTE' in permissions and len(gestiones) == 1:
        gestion_actual = gestiones[0]
        session['gestion_id'] = gestion_actual['id']
        session['gestion_nombre'] = gestion_actual['descrip']
        session['gestion_year'] = gestion_actual['gestion']
        session['moneda_base'] = gestion_actual['moneda']
        return redirect(url_for('dashboard.index'))

    # CONTADOR u otros: mostrar selector
    if request.method == 'POST':
        gestion_id = request.form.get('gestion_id')
        gestion = next((g for g in gestiones if str(g['id']) == gestion_id), None)
        if gestion:
            session['gestion_id'] = gestion['id']
            session['gestion_nombre'] = gestion['descrip']
            session['gestion_year'] = gestion['gestion']
            session['moneda_base'] = gestion['moneda']
            return redirect(url_for('dashboard.index'))
        else:
            flash('Debes seleccionar una gestión válida.', 'danger')

    return render_template('auth/select_gestion.html', gestiones=gestiones)

@auth_bp.route('/set-gestion/<int:gestion_id>')
def set_gestion(gestion_id):
    if 'empresa_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Obtener datos de la gestión
    gestiones = AuthModel.get_company_gestiones(session['empresa_id'])
    gestion_actual = next((g for g in gestiones if g['id'] == gestion_id), None)
    
    if gestion_actual:
        session['gestion_id'] = gestion_id
        session['gestion_nombre'] = gestion_actual['descrip']
        session['gestion_year'] = gestion_actual['gestion']
        session['moneda_base'] = gestion_actual['moneda']
        
        return redirect(url_for('dashboard.index'))
    
    flash('Gestión no encontrada', 'error')
    return redirect(url_for('auth.select_gestion'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('auth.login'))




@auth_bp.route('/cambiar-gestion-sidebar', methods=['POST'])
def cambiar_gestion_sidebar():
    gestion_id = request.form.get('gestion_id')
    gestiones = session.get('gestiones_disponibles', [])
    gestion = next((g for g in gestiones if str(g['id']) == gestion_id), None)
    if gestion:
        session['gestion_activa'] = gestion['id']
        session['gestion_nombre'] = gestion['descrip']
        session['gestion_year'] = gestion['gestion']
        session['moneda_base'] = gestion['moneda']
    else:
        flash('Debes seleccionar una gestión válida.', 'danger')
    return redirect(request.referrer or url_for('dashboard.index'))