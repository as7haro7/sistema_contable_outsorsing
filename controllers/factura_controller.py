from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.facture_model import FacturaModel
from models.tercero_model import TerceroModel
from utils.decorators import login_required, empresa_required

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

# === COMPRAS ===

@facturas_bp.route('/compras')
@login_required
@empresa_required
def compras():
    compras = FacturaModel.listar_compras()
    return render_template('iva/compras.html', compras=compras)

@facturas_bp.route('/compras/nueva', methods=['GET', 'POST'])
@login_required
@empresa_required
def nueva_compra():
    proveedores = TerceroModel.get_all('proveedor')
    if request.method == 'POST':
        data = request.form.to_dict()
        # Validar antes de registrar
        validacion = FacturaModel.validar_factura_compra(data)
        if not validacion['success']:
            flash(validacion['message'], 'danger')
            return render_template('iva/compras.html', proveedores=proveedores, data=data)
        resultado = FacturaModel.registrar_compra(data)
        if resultado['success']:
            flash('Factura de compra registrada correctamente', 'success')
            return redirect(url_for('facturas.compras'))
        else:
            flash(resultado['message'], 'danger')
            return render_template('iva/compras.html', proveedores=proveedores, data=data)
    return render_template('iva/compras.html', proveedores=proveedores)

@facturas_bp.route('/compras/anular/<int:factura_id>', methods=['POST'])
@login_required
@empresa_required
def anular_compra(factura_id):
    motivo = request.form.get('motivo', 'Anulación manual')
    resultado = FacturaModel.anular_compra(factura_id, motivo)
    if resultado['success']:
        flash('Factura anulada correctamente', 'success')
    else:
        flash(resultado['message'], 'danger')
    return redirect(url_for('facturas.compras'))

@facturas_bp.route('/compras/<int:factura_id>')
@login_required
@empresa_required
def detalle_compra(factura_id):
    compra = FacturaModel.obtener_compra(factura_id)
    if not compra:
        flash('Factura no encontrada', 'warning')
        return redirect(url_for('facturas.compras'))
    return render_template('iva/detalle_compra.html', compra=compra)

# === VENTAS ===

@facturas_bp.route('/ventas')
@login_required
@empresa_required
def ventas():
    ventas = FacturaModel.listar_ventas()
    return render_template('iva/ventas.html', ventas=ventas)

@facturas_bp.route('/ventas/nueva', methods=['GET', 'POST'])
@login_required
@empresa_required
def nueva_venta():
    clientes = TerceroModel.get_all('cliente')
    if request.method == 'POST':
        data = request.form.to_dict()
        validacion = FacturaModel.validar_factura_venta(data)
        if not validacion['success']:
            flash(validacion['message'], 'danger')
            return render_template('iva/ventas.html', clientes=clientes, data=data)
        resultado = FacturaModel.registrar_venta(data)
        if resultado['success']:
            flash('Factura de venta registrada correctamente', 'success')
            return redirect(url_for('facturas.ventas'))
        else:
            flash(resultado['message'], 'danger')
            return render_template('iva/ventas.html', clientes=clientes, data=data)
    return render_template('iva/ventas.html', clientes=clientes)

@facturas_bp.route('/ventas/anular/<int:factura_id>', methods=['POST'])
@login_required
@empresa_required
def anular_venta(factura_id):
    motivo = request.form.get('motivo', 'Anulación manual')
    resultado = FacturaModel.anular_venta(factura_id, motivo)
    if resultado['success']:
        flash('Factura anulada correctamente', 'success')
    else:
        flash(resultado['message'], 'danger')
    return redirect(url_for('facturas.ventas'))

@facturas_bp.route('/ventas/<int:factura_id>')
@login_required
@empresa_required
def detalle_venta(factura_id):
    venta = FacturaModel.obtener_venta(factura_id)
    if not venta:
        flash('Factura no encontrada', 'warning')
        return redirect(url_for('facturas.ventas'))
    return render_template('iva/detalle_venta.html', venta=venta)

# Puedes agregar más rutas para detalles, edición, reportes, etc.