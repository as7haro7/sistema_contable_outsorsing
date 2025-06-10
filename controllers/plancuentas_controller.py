from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models.plancuenta_model import PlancuentaModel
from utils.decorators import login_required, empresa_required
import logging

logger = logging.getLogger(__name__)

plancuentas_bp = Blueprint('plancuentas', __name__, url_prefix='/plancuentas')

@plancuentas_bp.route('/')
@login_required
@empresa_required
def index():
    """Página principal del plan de cuentas con vista de árbol"""
    try:
        empresa_id = session.get('empresa_id')
        if not empresa_id:
            flash('No hay empresa activa en la sesión', 'error')
            return redirect(url_for('dashboard.index'))
        arbol_cuentas = PlancuentaModel.obtener_arbol_cuentas(empresa_id)
        return render_template('contabilidad/plancuentas/index.html', arbol_cuentas=arbol_cuentas)
    except Exception as e:
        import traceback
        logger.error(f"Error en plancuentas index: {e}\n{traceback.format_exc()}")
        flash('Error al cargar el plan de cuentas', 'error')
        return redirect(url_for('dashboard.index'))

@plancuentas_bp.route('/detalle/<codigo>')
@login_required
@empresa_required
def detalle(codigo):
    """Detalle de una cuenta específica"""
    try:
        empresa_id = session.get('empresa_id')
        cuenta = PlancuentaModel.obtener_cuenta_por_codigo(empresa_id, str(codigo))
        if cuenta:
            return render_template('contabilidad/plancuentas/detalle.html', cuenta=cuenta)
        else:
            flash('Cuenta no encontrada', 'error')
            return redirect(url_for('plancuentas.index'))
    except Exception as e:
        logger.error(f"Error al obtener cuenta {codigo}: {e}")
        flash('Error al obtener cuenta', 'error')
        return redirect(url_for('plancuentas.index'))

@plancuentas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@empresa_required
def crear():
    """Crear nueva cuenta contable"""
    empresa_id = session.get('empresa_id')
    if request.method == 'GET':
        try:
            niveles = PlancuentaModel.obtener_niveles(empresa_id)
            tipos_cuenta = PlancuentaModel.obtener_tipos_cuenta(empresa_id)
            tipos_movimiento = PlancuentaModel.obtener_tipos_movimiento(empresa_id)
            monedas = PlancuentaModel.obtener_monedas(empresa_id)
            return render_template('contabilidad/plancuentas/create.html',
                                   niveles=niveles,
                                   tipos_cuenta=tipos_cuenta,
                                   tipos_movimiento=tipos_movimiento,
                                   monedas=monedas)
        except Exception as e:
            logger.error(f"Error al cargar formulario de creación: {e}")
            flash('Error al cargar el formulario', 'error')
            return redirect(url_for('plancuentas.index'))
    else:  # POST
        try:
            # modificar esto, no obitiene el usuario de la sesión
            usuario = session.get('user_nombre') or session.get('usuario') or 'admin'
            datos = {
                'cuenta': request.form.get('cuenta', '').strip(),
                'descrip': request.form.get('descrip', '').strip(),
                'tipo_cuenta': request.form.get('tipo_cuenta'),
                'nivel': request.form.get('nivel'),
                'tipomov': request.form.get('tipomov'),
                'moneda': request.form.get('moneda')
            }
            es_valido, mensaje = PlancuentaModel.validar_estructura_cuenta(datos['cuenta'])
            if not es_valido:
                flash(mensaje, 'error')
                return redirect(url_for('plancuentas.crear'))
            resultado = PlancuentaModel.crear_cuenta(empresa_id, datos, usuario)
            if resultado['success']:
                flash(resultado['message'], 'success')
                return redirect(url_for('plancuentas.index'))
            else:
                flash(resultado['message'], 'error')
                return redirect(url_for('plancuentas.crear'))
        except Exception as e:
            logger.error(f"Error al crear cuenta: {e}")
            flash('Error al crear la cuenta', 'error')
            return redirect(url_for('plancuentas.crear'))

@plancuentas_bp.route('/editar/<codigo>', methods=['GET', 'POST'])
@login_required
@empresa_required
def editar(codigo):
    """Editar cuenta contable existente"""
    empresa_id = session.get('empresa_id')
    codigo = str(codigo).strip()  # <-- Asegura que el código esté limpio
    if request.method == 'GET':
        try:
            cuenta = PlancuentaModel.obtener_cuenta_por_codigo(empresa_id, codigo)
            if not cuenta:
                flash('Cuenta no encontrada', 'error')
                return redirect(url_for('plancuentas.index'))
            if PlancuentaModel.tiene_movimientos(empresa_id, codigo):
                flash('No se puede editar una cuenta con movimientos registrados', 'warning')
                return redirect(url_for('plancuentas.index'))
            niveles = PlancuentaModel.obtener_niveles(empresa_id)
            tipos_cuenta = PlancuentaModel.obtener_tipos_cuenta(empresa_id)
            tipos_movimiento = PlancuentaModel.obtener_tipos_movimiento(empresa_id)
            monedas = PlancuentaModel.obtener_monedas(empresa_id)
            return render_template('contabilidad/plancuentas/edit.html',
                                   cuenta=cuenta,
                                   niveles=niveles,
                                   tipos_cuenta=tipos_cuenta,
                                   tipos_movimiento=tipos_movimiento,
                                   monedas=monedas)
        except Exception as e:
            logger.error(f"Error al cargar formulario de edición: {e}")
            flash('Error al cargar el formulario', 'error')
            return redirect(url_for('plancuentas.index'))
    else:  # POST
        try:
            # modificar esto, no obitiene el usuario de la sesión
            usuario = session.get('user_nombre') or session.get('usuario') or 'admin'
            datos = {
                'descrip': request.form.get('descrip', '').strip(),
                'tipo_cuenta': request.form.get('tipo_cuenta'),
                'nivel': request.form.get('nivel'),
                'tipomov': request.form.get('tipomov'),
                'moneda': request.form.get('moneda')
            }
            resultado = PlancuentaModel.actualizar_cuenta(empresa_id, codigo, datos, usuario)
            if resultado['success']:
                flash(resultado['message'], 'success')
                return redirect(url_for('plancuentas.index'))
            else:
                flash(resultado['message'], 'error')
                return redirect(url_for('plancuentas.editar', codigo=codigo))
        except Exception as e:
            logger.error(f"Error al actualizar cuenta: {e}")
            flash('Error al actualizar la cuenta', 'error')
            return redirect(url_for('plancuentas.editar', codigo=codigo))

@plancuentas_bp.route('/eliminar/<codigo>', methods=['POST'])
@login_required
@empresa_required
def eliminar(codigo):
    """Eliminar una cuenta contable"""
    try:
        empresa_id = session.get('empresa_id')
        resultado = PlancuentaModel.eliminar_cuenta(empresa_id, codigo)
        if resultado['success']:
            flash(resultado['message'], 'success')
        else:
            flash(resultado['message'], 'error')
        return redirect(url_for('plancuentas.index'))
    except Exception as e:
        logger.error(f"Error al eliminar cuenta {codigo}: {e}")
        flash('Error al eliminar la cuenta', 'error')
        return redirect(url_for('plancuentas.index'))