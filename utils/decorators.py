from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def empresa_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'empresa_id' not in session or 'gestion_id' not in session:
            return redirect(url_for('auth.select_empresa'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(modulo):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            permissions = session.get('permissions', {})
            if modulo not in permissions:
                flash('No tiene permisos para acceder a este módulo', 'error')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator