from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.asiento_model import AsientoModel
from utils.decorators import login_required, empresa_required
from datetime import datetime, date
import json

asientos_bp = Blueprint('asientos', __name__, url_prefix='/asientos')

@asientos_bp.route('/')
@login_required
@empresa_required
def index():
    """Lista los asientos con filtros opcionales"""
    try:
        # Obtener parámetros de filtro desde la URL
        filtro = {}
        
        if request.args.get('fecha_desde'):
            filtro['fecha_desde'] = request.args.get('fecha_desde')
        
        if request.args.get('fecha_hasta'):
            filtro['fecha_hasta'] = request.args.get('fecha_hasta')
        
        if request.args.get('tipo'):
            filtro['tipo'] = request.args.get('tipo')
        
        if request.args.get('estado'):
            filtro['estado'] = request.args.get('estado')
        
        if request.args.get('codigo'):
            filtro['codigo'] = request.args.get('codigo')
        
        # Obtener asientos con filtros
        asientos = AsientoModel.obtener_asientos(filtro if filtro else None)
        tipos_asiento = AsientoModel.obtener_tipos_asiento()
        
        return render_template('contabilidad/asientos/index.html', 
                             asientos=asientos, 
                             tipos_asiento=tipos_asiento,
                             filtro=filtro)
    except Exception as e:
        flash(f'Error al cargar asientos: {str(e)}', 'error')
        return render_template('contabilidad/asientos/index.html', asientos=[], tipos_asiento=[])

@asientos_bp.route('/ver/<codigo>')
@login_required
@empresa_required
def ver(codigo):
    """Ver detalles de un asiento específico"""
    try:
        asiento_data = AsientoModel.obtener_asiento_por_codigo(codigo)
        if not asiento_data:
            flash('Asiento no encontrado', 'error')
            return redirect(url_for('asientos.index'))
        
        return render_template('contabilidad/asientos/detalle.html', 
                             asiento=asiento_data['asiento'], 
                             detalles=asiento_data['detalles'])
    except Exception as e:
        flash(f'Error al cargar asiento: {str(e)}', 'error')
        return redirect(url_for('asientos.index'))

@asientos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@empresa_required
def crear():
    """Crear un nuevo asiento contable"""
    if request.method == 'GET':
        # Cargar datos para el formulario
        tipos_asiento = AsientoModel.obtener_tipos_asiento()
        cuentas = AsientoModel.obtener_cuentas_activas()
        centros_costos = AsientoModel.obtener_centros_costos()
        
        # Generar código sugerido (opcional)
        codigo_sugerido = ""
        if request.args.get('tipo'):
            fecha_actual = datetime.now().date()
            codigo_sugerido = AsientoModel.generar_codigo_asiento(request.args.get('tipo'), fecha_actual)
        
        return render_template('contabilidad/asientos/create.html', 
                             tipos_asiento=tipos_asiento, 
                             cuentas=cuentas, 
                             centros_costos=centros_costos,
                             codigo_sugerido=codigo_sugerido,
                             fecha_actual=datetime.now().strftime('%Y-%m-%d'))
    
    # POST - Procesar creación
    try:
        usuario = session.get('user_nombre', 'sistema')
        
        # Obtener datos del asiento principal
        data = {
            'codigo': request.form.get('codigo'),  # Puede ser None para auto-generar
            'cta': request.form.get('cta'),
            'tipo': request.form.get('tipo'),
            'secuencia': int(request.form.get('secuencia', 0)),
            'srs': request.form.get('srs'),
            'glosa': request.form.get('glosa'),
            'fecha': datetime.strptime(request.form.get('fecha'), '%Y-%m-%d').date(),
            'estado': 'BORRADOR'
        }
        
        # Validar datos requeridos
        if not data['tipo']:
            flash('El tipo de asiento es requerido', 'error')
            return redirect(url_for('asientos.crear'))
        
        if not data['glosa']:
            flash('La glosa es requerida', 'error')
            return redirect(url_for('asientos.crear'))
        
        # Procesar detalles del asiento
        detalles = []
        cuentas_det = request.form.getlist('cuenta')
        items = request.form.getlist('item')
        debebs_list = request.form.getlist('debebs')
        haberbs_list = request.form.getlist('haberbs')
        debesus_list = request.form.getlist('debesus')
        habersus_list = request.form.getlist('habersus')
        cencostos_list = request.form.getlist('cencosto')
        referencias_list = request.form.getlist('referencia')
        
        for i in range(len(cuentas_det)):
            if cuentas_det[i]:  # Solo procesar si hay cuenta
                detalle = {
                    'cuenta': cuentas_det[i],
                    'item': items[i] if i < len(items) and items[i] else None,
                    'debebs': float(debebs_list[i]) if i < len(debebs_list) and debebs_list[i] else 0,
                    'haberbs': float(haberbs_list[i]) if i < len(haberbs_list) and haberbs_list[i] else 0,
                    'debesus': float(debesus_list[i]) if i < len(debesus_list) and debesus_list[i] else 0,
                    'habersus': float(habersus_list[i]) if i < len(habersus_list) and habersus_list[i] else 0,
                    'cencosto': cencostos_list[i] if i < len(cencostos_list) and cencostos_list[i] else None,
                    'referencia': referencias_list[i] if i < len(referencias_list) and referencias_list[i] else None,
                    'orden': i + 1
                }
                detalles.append(detalle)
        
        if not detalles:
            flash('Debe agregar al menos un detalle al asiento', 'error')
            return redirect(url_for('asientos.crear'))
        
        # Crear el asiento
        resultado = AsientoModel.crear_asiento(data, detalles, usuario)
        
        if resultado['success']:
            flash(resultado['message'], 'success')
            return redirect(url_for('asientos.ver', codigo=resultado['codigo']))
        else:
            flash(resultado['message'], 'error')
            
    except ValueError as ve:
        flash(f'Error en los datos proporcionados: {str(ve)}', 'error')
    except Exception as e:
        flash(f'Error al crear asiento: {str(e)}', 'error')
    
    return redirect(url_for('asientos.crear'))

@asientos_bp.route('/editar/<codigo>', methods=['GET', 'POST'])
@login_required
@empresa_required
def editar(codigo):
    """Editar un asiento existente"""
    try:
        asiento_data = AsientoModel.obtener_asiento_por_codigo(codigo)
        if not asiento_data:
            flash('Asiento no encontrado', 'error')
            return redirect(url_for('asientos.index'))
        
        asiento = asiento_data['asiento']
        
        # Verificar que se pueda editar
        if asiento['estado'] != 'BORRADOR':
            flash('Solo se pueden editar asientos en borrador', 'error')
            return redirect(url_for('asientos.ver', codigo=codigo))
        
        if request.method == 'GET':
            tipos_asiento = AsientoModel.obtener_tipos_asiento()
            cuentas = AsientoModel.obtener_cuentas_activas()
            centros_costos = AsientoModel.obtener_centros_costos()
            
            return render_template('contabilidad/asientos/edit.html', 
                                 asiento=asiento, 
                                 detalles=asiento_data['detalles'], 
                                 tipos_asiento=tipos_asiento, 
                                 cuentas=cuentas, 
                                 centros_costos=centros_costos)
        
        # POST - Procesar actualización
        usuario = session.get('user_nombre', 'sistema')
        
        # Obtener datos actualizados del asiento
        data = {
            'cta': request.form.get('cta'),
            'tipo': request.form.get('tipo'),
            'secuencia': int(request.form.get('secuencia', 0)),
            'srs': request.form.get('srs'),
            'glosa': request.form.get('glosa'),
            'fecha': datetime.strptime(request.form.get('fecha'), '%Y-%m-%d').date()
        }
        
        # Procesar detalles actualizados
        detalles = []
        cuentas_det = request.form.getlist('cuenta')
        items = request.form.getlist('item')
        debebs_list = request.form.getlist('debebs')
        haberbs_list = request.form.getlist('haberbs')
        debesus_list = request.form.getlist('debesus')
        habersus_list = request.form.getlist('habersus')
        cencostos_list = request.form.getlist('cencosto')
        referencias_list = request.form.getlist('referencia')
        
        for i in range(len(cuentas_det)):
            if cuentas_det[i]:
                detalle = {
                    'cuenta': cuentas_det[i],
                    'item': items[i] if i < len(items) and items[i] else None,
                    'debebs': float(debebs_list[i]) if i < len(debebs_list) and debebs_list[i] else 0,
                    'haberbs': float(haberbs_list[i]) if i < len(haberbs_list) and haberbs_list[i] else 0,
                    'debesus': float(debesus_list[i]) if i < len(debesus_list) and debesus_list[i] else 0,
                    'habersus': float(habersus_list[i]) if i < len(habersus_list) and habersus_list[i] else 0,
                    'cencosto': cencostos_list[i] if i < len(cencostos_list) and cencostos_list[i] else None,
                    'referencia': referencias_list[i] if i < len(referencias_list) and referencias_list[i] else None,
                    'orden': i + 1
                }
                detalles.append(detalle)
        
        if not detalles:
            flash('Debe agregar al menos un detalle al asiento', 'error')
            return redirect(url_for('asientos.editar', codigo=codigo))
        
        # Actualizar el asiento
        resultado = AsientoModel.actualizar_asiento(codigo, data, detalles, usuario)
        
        if resultado['success']:
            flash(resultado['message'], 'success')
            return redirect(url_for('asientos.ver', codigo=codigo))
        else:
            flash(resultado['message'], 'error')
            
    except ValueError as ve:
        flash(f'Error en los datos proporcionados: {str(ve)}', 'error')
    except Exception as e:
        flash(f'Error al editar asiento: {str(e)}', 'error')
    
    return redirect(url_for('asientos.editar', codigo=codigo))

@asientos_bp.route('/confirmar/<codigo>', methods=['POST'])
@login_required
@empresa_required
def confirmar(codigo):
    """Confirmar un asiento (cambiar estado a CONFIRMADO)"""
    try:
        usuario = session.get('user_nombre', 'sistema')
        resultado = AsientoModel.confirmar_asiento(codigo, usuario)
        
        if resultado['success']:
            flash(resultado['message'], 'success')
        else:
            flash(resultado['message'], 'error')
            
    except Exception as e:
        flash(f'Error al confirmar asiento: {str(e)}', 'error')
    
    return redirect(url_for('asientos.ver', codigo=codigo))

@asientos_bp.route('/anular/<codigo>', methods=['POST'])
@login_required
@empresa_required
def anular(codigo):
    """Anular un asiento"""
    try:
        usuario = session.get('user_nombre', 'sistema')
        resultado = AsientoModel.anular_asiento(codigo, usuario)
        
        if resultado['success']:
            flash(resultado['message'], 'success')
        else:
            flash(resultado['message'], 'error')
            
    except Exception as e:
        flash(f'Error al anular asiento: {str(e)}', 'error')
    
    return redirect(url_for('asientos.index'))

@asientos_bp.route('/generar_codigo')
@login_required
@empresa_required
def generar_codigo():
    """Endpoint AJAX para generar código de asiento"""
    try:
        tipo = request.args.get('tipo')
        fecha_str = request.args.get('fecha')
        
        if not tipo:
            return jsonify({'success': False, 'message': 'Tipo requerido'})
        
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else datetime.now().date()
        codigo = AsientoModel.generar_codigo_asiento(tipo, fecha)
        
        if codigo:
            return jsonify({'success': True, 'codigo': codigo})
        else:
            return jsonify({'success': False, 'message': 'Error al generar código'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@asientos_bp.route('/validar_partida_doble', methods=['POST'])
@login_required
@empresa_required
def validar_partida_doble():
    """Endpoint AJAX para validar partida doble"""
    try:
        data = request.get_json()
        detalles = data.get('detalles', [])
        
        es_valida, mensaje = AsientoModel.validar_partida_doble(detalles)
        
        return jsonify({
            'success': True,
            'es_valida': es_valida,
            'mensaje': mensaje
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@asientos_bp.route('/balance_comprobacion')
@login_required
@empresa_required
def balance_comprobacion():
    """Generar balance de comprobación"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        if not fecha_desde or not fecha_hasta:
            # Valores por defecto: primer y último día del mes actual
            hoy = datetime.now().date()
            fecha_desde = hoy.replace(day=1).strftime('%Y-%m-%d')
            fecha_hasta = hoy.strftime('%Y-%m-%d')
        
        balance = AsientoModel.obtener_balance_comprobacion(fecha_desde, fecha_hasta)
        
        return render_template('contabilidad/reportes/balance_comprobacion.html',
                             balance=balance,
                             fecha_desde=fecha_desde,
                             fecha_hasta=fecha_hasta)
        
    except Exception as e:
        flash(f'Error al generar balance de comprobación: {str(e)}', 'error')
        return redirect(url_for('asientos.index'))

# @asientos_bp.route('/api/cuentas')
# @login_required
# @empresa_required
# def api_cuentas():
#     """API endpoint para obtener cuentas (para uso con AJAX)"""
#     try:
#         cuentas = AsientoModel.obtener_cuentas_activas()
#         return jsonify({'success': True, 'cuentas': cuentas})
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)})

# @asientos_bp.route('/api/centros_costos')
# @login_required
# @empresa_required
# def api_centros_costos():
#     """API endpoint para obtener centros de costos (para uso con AJAX)"""
#     try:
#         centros = AsientoModel.obtener_centros_costos()
#         return jsonify({'success': True, 'centros_costos': centros})
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}')

# # Filtros de plantilla personalizados
# @asientos_bp.app_template_filter('formato_moneda')
# def formato_moneda(valor):
#     """Formatea un valor como moneda"""
#     try:
#         return f"{float(valor):,.2f}" if valor else "0.00"
#     except (ValueError, TypeError):
#         return "0.00"

# @asientos_bp.app_template_filter('formato_fecha')
# def formato_fecha(fecha):
#     """Formatea una fecha"""
#     try:
#         if isinstance(fecha, str):
#             fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
#         return fecha.strftime('%d/%m/%Y')
#     except Exception:
#         return fecha