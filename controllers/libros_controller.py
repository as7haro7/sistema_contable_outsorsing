from flask import Blueprint, render_template, request, session, flash, jsonify, redirect, url_for
from models.libro_model import LibroModel
from utils.decorators import login_required, empresa_required
from datetime import datetime, date
import logging

# Configurar logging
logger = logging.getLogger(__name__)

libros_bp = Blueprint('libros', __name__, url_prefix='/libros')

@libros_bp.route('/')
@login_required
@empresa_required
def index():
    """Página principal de libros contables"""
    return render_template('contabilidad/libros/index.html')

@libros_bp.route('/diario')
@login_required
@empresa_required
def libro_diario():
    """Libro Diario - Lista cronológica de todos los asientos"""
    try:
        # Obtener parámetros de filtro
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        cuenta = request.args.get('cuenta')
        tipo_asiento = request.args.get('tipo_asiento')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Validar fechas
        if fecha_desde:
            try:
                datetime.strptime(fecha_desde, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha desde inválido', 'error')
                fecha_desde = None
                
        if fecha_hasta:
            try:
                datetime.strptime(fecha_hasta, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha hasta inválido', 'error')
                fecha_hasta = None
        
        # Obtener datos del libro diario
        asientos = LibroModel.get_libro_diario(
            fecha_desde=fecha_desde, 
            fecha_hasta=fecha_hasta, 
            cuenta=cuenta, 
            tipo_asiento=tipo_asiento
        )
        
        # Obtener datos auxiliares para filtros
        tipos_asiento = LibroModel.get_tipos_asiento()
        cuentas_con_movimientos = LibroModel.get_cuentas_con_movimientos(fecha_desde, fecha_hasta)
        
        # Calcular totales generales
        total_debe = sum(asiento.get('total_debe_bs', 0) for asiento in asientos)
        total_haber = sum(asiento.get('total_haber_bs', 0) for asiento in asientos)
        
        return render_template('contabilidad/libros/diario.html', 
                             asientos=asientos,
                             tipos_asiento=tipos_asiento,
                             cuentas_con_movimientos=cuentas_con_movimientos,
                             fecha_desde=fecha_desde, 
                             fecha_hasta=fecha_hasta,
                             cuenta=cuenta,
                             tipo_asiento=tipo_asiento,
                             total_debe=total_debe,
                             total_haber=total_haber,
                             page=page,
                             per_page=per_page)
                             
    except Exception as e:
        logger.error(f"Error en libro_diario: {str(e)}")
        flash('Error al cargar el libro diario', 'error')
        # return render_template('contabilidad/libros/diario.html', asientos={'items': [], 'total': 0})
    return render_template('contabilidad/libros/diario.html', asientos=[], total_debe=0, total_haber=0, tipos_asiento=[], cuentas_con_movimientos=[])

@libros_bp.route('/mayor')
@login_required
@empresa_required
def libro_mayor():
    """Libro Mayor - Agrupación por cuenta contable"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        cuenta = request.args.get('cuenta')
        solo_con_saldo = request.args.get('solo_con_saldo', 'false') == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Obtener datos del libro mayor
        mayor = LibroModel.get_libro_mayor(
            fecha_desde=fecha_desde, 
            fecha_hasta=fecha_hasta, 
            cuenta=cuenta,
            solo_con_movimientos=solo_con_saldo
        )
        
        # Obtener saldos iniciales si hay fecha desde
        saldos_iniciales = None
        if fecha_desde:
            saldos_iniciales = LibroModel.get_saldos_iniciales(fecha_desde)
        
        # Obtener cuentas para filtro
        cuentas_con_movimientos = LibroModel.get_cuentas_con_movimientos(fecha_desde, fecha_hasta)
        
        return render_template('contabilidad/libros/mayor.html', 
                             mayor=mayor,
                             saldos_iniciales=saldos_iniciales,
                             cuentas_con_movimientos=cuentas_con_movimientos,
                             fecha_desde=fecha_desde, 
                             fecha_hasta=fecha_hasta,
                             cuenta=cuenta,
                             solo_con_saldo=solo_con_saldo,
                             page=page,
                             per_page=per_page)
                             
    except Exception as e:
        logger.error(f"Error en libro_mayor: {str(e)}")
        flash('Error al cargar el libro mayor', 'error')
        return render_template('contabilidad/libros/mayor.html', mayor={})

@libros_bp.route('/balance_comprobacion')
@login_required
@empresa_required
def balance_comprobacion():
    """Balance de Comprobación"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        nivel_detalle = request.args.get('nivel_detalle', 'todos')  # todos, mayor, auxiliar
        solo_con_movimiento = request.args.get('solo_con_movimiento', 'false') == 'true'
        
        # Validar que al menos fecha_hasta esté presente
        if not fecha_hasta:
            fecha_hasta = date.today().strftime('%Y-%m-%d')
        
        balance = LibroModel.get_balance_comprobacion(
            fecha_desde=fecha_desde, 
            fecha_hasta=fecha_hasta
        )
                
        # Calcular totales
        total_saldo_inicial = sum(item.get('saldo_bs', 0) for item in balance)
        total_debe = sum(item.get('total_debe_bs', 0) for item in balance)
        total_haber = sum(item.get('total_haber_bs', 0) for item in balance)
        total_saldo_final = sum(item.get('saldo_bs', 0) for item in balance)
        
        return render_template('contabilidad/libros/balance_comprobacion.html', 
                             balance=balance,
                             fecha_desde=fecha_desde, 
                             fecha_hasta=fecha_hasta,
                             nivel_detalle=nivel_detalle,
                             solo_con_movimiento=solo_con_movimiento,
                             total_saldo_inicial=total_saldo_inicial,
                             total_debe=total_debe,
                             total_haber=total_haber,
                             total_saldo_final=total_saldo_final)
                             
    except Exception as e:
        logger.error(f"Error en balance_comprobacion: {str(e)}")
        flash('Error al cargar el balance de comprobación', 'error')
        return render_template(
            'contabilidad/libros/balance_comprobacion.html',
            balance=[],
            fecha_desde=None,
            fecha_hasta=None,
            nivel_detalle=None,
            solo_con_movimiento=None,
            total_saldo_inicial=0,
            total_debe=0,
            total_haber=0,
            total_saldo_final=0
        )

@libros_bp.route('/balance_general')
@login_required
@empresa_required
def balance_general():
    """Balance General - Estado de Situación Financiera"""
    try:
        fecha_hasta = request.args.get('fecha_hasta')
        moneda = request.args.get('moneda', 'BOB')
        comparativo = request.args.get('comparativo', 'false') == 'true'
        fecha_comparacion = request.args.get('fecha_comparacion')
        
        if not fecha_hasta:
            fecha_hasta = date.today().strftime('%Y-%m-%d')
        
        balance = LibroModel.get_balance_general(fecha_hasta, moneda)
        
        # Si es comparativo, obtener datos de fecha anterior
        balance_anterior = None
        if comparativo and fecha_comparacion:
            balance_anterior = LibroModel.get_balance_general(fecha_comparacion, moneda)
        
        # Agrupar por tipo de cuenta
        activos = [item for item in balance if item.get('tipo_cuenta') == 'ACTIVO']
        pasivos = [item for item in balance if item.get('tipo_cuenta') == 'PASIVO']
        patrimonio = [item for item in balance if item.get('tipo_cuenta') == 'PATRIMONIO']
        
        # Calcular totales
        total_activos = sum(item.get('saldo', 0) for item in activos)
        total_pasivos = sum(item.get('saldo', 0) for item in pasivos)
        total_patrimonio = sum(item.get('saldo', 0) for item in patrimonio)
        
        return render_template('contabilidad/libros/balance_general.html', 
                             balance=balance,
                             balance_anterior=balance_anterior,
                             activos=activos,
                             pasivos=pasivos,
                             patrimonio=patrimonio,
                             total_activos=total_activos,
                             total_pasivos=total_pasivos,
                             total_patrimonio=total_patrimonio,
                             fecha_hasta=fecha_hasta,
                             fecha_comparacion=fecha_comparacion,
                             moneda=moneda,
                             comparativo=comparativo)
                             
    except Exception as e:
        logger.error(f"Error en balance_general: {str(e)}")
        flash('Error al cargar el balance general', 'error')
        return render_template('contabilidad/libros/balance_general.html', balance=[])

@libros_bp.route('/estado_resultados')
@login_required
@empresa_required
def estado_resultados():
    """Estado de Resultados - P&G"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        moneda = request.args.get('moneda', 'BOB')
        tipo_periodo = request.args.get('tipo_periodo', 'personalizado')  # mensual, trimestral, anual, personalizado
        
        # Manejar períodos predefinidos
        if tipo_periodo != 'personalizado':
            fecha_desde, fecha_hasta = _calcular_periodo(tipo_periodo)
        
        if not fecha_hasta:
            fecha_hasta = date.today().strftime('%Y-%m-%d')
        if not fecha_desde:
            fecha_desde = date.today().replace(month=1, day=1).strftime('%Y-%m-%d')
        
        resultados = LibroModel.get_estado_resultados(fecha_desde, fecha_hasta, moneda)
        
        # Agrupar por tipo
        ingresos = [item for item in resultados if item.get('tipo_cuenta') == 'INGRESO']
        gastos = [item for item in resultados if item.get('tipo_cuenta') == 'GASTO']
        costos = [item for item in resultados if item.get('tipo_cuenta') == 'COSTO']
        
        # Calcular totales y utilidades
        total_ingresos = sum(abs(item.get('saldo', 0)) for item in ingresos)
        total_costos = sum(abs(item.get('saldo', 0)) for item in costos)
        total_gastos = sum(abs(item.get('saldo', 0)) for item in gastos)
        
        utilidad_bruta = total_ingresos - total_costos
        utilidad_neta = utilidad_bruta - total_gastos
        
        return render_template('contabilidad/libros/estado_resultados.html', 
                             resultados=resultados,
                             ingresos=ingresos,
                             gastos=gastos,
                             costos=costos,
                             total_ingresos=total_ingresos,
                             total_costos=total_costos,
                             total_gastos=total_gastos,
                             utilidad_bruta=utilidad_bruta,
                             utilidad_neta=utilidad_neta,
                             fecha_desde=fecha_desde, 
                             fecha_hasta=fecha_hasta,
                             moneda=moneda,
                             tipo_periodo=tipo_periodo)
                             
    except Exception as e:
        logger.error(f"Error en estado_resultados: {str(e)}")
        flash('Error al cargar el estado de resultados', 'error')
        return render_template('contabilidad/libros/estado_resultados.html', resultados=[])

@libros_bp.route('/resumen_periodo')
@login_required
@empresa_required
def resumen_periodo():
    """Resumen estadístico del período"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        if not fecha_hasta:
            fecha_hasta = date.today().strftime('%Y-%m-%d')
        if not fecha_desde:
            fecha_desde = date.today().replace(month=1, day=1).strftime('%Y-%m-%d')
        
        resumen = LibroModel.get_resumen_periodo(fecha_desde, fecha_hasta)
        
        return render_template('contabilidad/libros/resumen_periodo.html', 
                             resumen=resumen,
                             fecha_desde=fecha_desde, 
                             fecha_hasta=fecha_hasta)
                             
    except Exception as e:
        logger.error(f"Error en resumen_periodo: {str(e)}")
        flash('Error al cargar el resumen del período', 'error')
        return render_template('contabilidad/libros/resumen_periodo.html', resumen={})

# Rutas AJAX para obtener datos dinámicamente
@libros_bp.route('/api/cuentas_con_movimientos')
@login_required
@empresa_required
def api_cuentas_con_movimientos():
    """API para obtener cuentas con movimientos (AJAX)"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        cuentas = LibroModel.get_cuentas_con_movimientos(fecha_desde, fecha_hasta)
        
        return jsonify({
            'success': True,
            'cuentas': cuentas
        })
        
    except Exception as e:
        logger.error(f"Error en api_cuentas_con_movimientos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error al obtener cuentas'
        }), 500

@libros_bp.route('/api/tipos_asiento')
@login_required
@empresa_required
def api_tipos_asiento():
    """API para obtener tipos de asiento (AJAX)"""
    try:
        tipos = LibroModel.get_tipos_asiento()
        
        return jsonify({
            'success': True,
            'tipos': tipos
        })
        
    except Exception as e:
        logger.error(f"Error en api_tipos_asiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error al obtener tipos de asiento'
        }), 500

@libros_bp.route('/api/saldos_iniciales')
@login_required
@empresa_required
def api_saldos_iniciales():
    """API para obtener saldos iniciales hasta una fecha"""
    try:
        fecha = request.args.get('fecha')
        if not fecha:
            return jsonify({
                'success': False,
                'error': 'Fecha requerida'
            }), 400
        
        saldos = LibroModel.get_saldos_iniciales(fecha)
        
        return jsonify({
            'success': True,
            'saldos': saldos
        })
        
    except Exception as e:
        logger.error(f"Error en api_saldos_iniciales: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error al obtener saldos iniciales'
        }), 500

# Rutas de exportación
@libros_bp.route('/exportar/<tipo_libro>')
@login_required
@empresa_required
def exportar_libro(tipo_libro):
    """Exportar libros a PDF o Excel"""
    try:
        formato = request.args.get('formato', 'pdf')  # pdf, excel
        
        if tipo_libro not in ['diario', 'mayor', 'balance_comprobacion', 'balance_general', 'estado_resultados']:
            flash('Tipo de libro no válido', 'error')
            return redirect(url_for('libros.index'))
        
        # Redirigir a la función específica de exportación
        if formato == 'pdf':
            return redirect(url_for(f'libros.exportar_{tipo_libro}_pdf', **request.args))
        else:
            return redirect(url_for(f'libros.exportar_{tipo_libro}_excel', **request.args))
            
    except Exception as e:
        logger.error(f"Error en exportar_libro: {str(e)}")
        flash('Error al exportar el libro', 'error')
        return redirect(url_for('libros.index'))

# Funciones auxiliares
def _calcular_periodo(tipo_periodo):
    """Calcular fechas para períodos predefinidos"""
    hoy = date.today()
    
    if tipo_periodo == 'mensual':
        fecha_desde = hoy.replace(day=1)
        fecha_hasta = hoy
    elif tipo_periodo == 'trimestral':
        mes_actual = hoy.month
        trimestre = ((mes_actual - 1) // 3) + 1
        mes_inicio = (trimestre - 1) * 3 + 1
        fecha_desde = hoy.replace(month=mes_inicio, day=1)
        fecha_hasta = hoy
    elif tipo_periodo == 'anual':
        fecha_desde = hoy.replace(month=1, day=1)
        fecha_hasta = hoy
    else:
        fecha_desde = hoy.replace(month=1, day=1)
        fecha_hasta = hoy
    
    return fecha_desde.strftime('%Y-%m-%d'), fecha_hasta.strftime('%Y-%m-%d')

# Manejo de errores específicos
@libros_bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@libros_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno en libros: {str(error)}")
    return render_template('errors/500.html'), 500