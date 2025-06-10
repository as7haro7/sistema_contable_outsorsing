from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from utils.decorators import login_required, permission_required, empresa_required

descargas_bp = Blueprint('descargas', __name__)

@descargas_bp.route('/descargas')
@login_required
@empresa_required
@permission_required('CLIENTE')
def index():
    # Aquí iría la lógica para obtener todos los archivos disponibles para descargar
    return render_template('cliente/descargas/index.html')

@descargas_bp.route('/descargas/estados-financieros')
@login_required
@empresa_required
@permission_required('CLIENTE')
def estados_financieros():
    # Aquí iría la lógica para obtener los estados financieros disponibles para descargar
    return render_template('cliente/descargas/estados_financieros.html')

@descargas_bp.route('/descargas/reportes')
@login_required
@empresa_required
@permission_required('CLIENTE')
def reportes():
    # Aquí iría la lógica para obtener los reportes disponibles para descargar
    return render_template('cliente/descargas/reportes.html')

@descargas_bp.route('/descargas/facturas')
@login_required
@empresa_required
@permission_required('CLIENTE')
def facturas():
    # Aquí iría la lógica para obtener las facturas disponibles para descargar
    return render_template('cliente/descargas/facturas.html')

@descargas_bp.route('/descargas/otros')
@login_required
@empresa_required
@permission_required('CLIENTE')
def otros():
    # Aquí iría la lógica para obtener otros documentos disponibles para descargar
    return render_template('cliente/descargas/otros.html')

@descargas_bp.route('/descargas/archivo/<int:id>')
@login_required
@empresa_required
@permission_required('CLIENTE')
def descargar_archivo(id):
    # Aquí iría la lógica para descargar un archivo específico
    # Ejemplo: return send_file(path, as_attachment=True)
    return redirect(url_for('descargas.index'))

# Rutas para el contador (subir archivos)
@descargas_bp.route('/archivos')
@login_required
@empresa_required
@permission_required('CONTADOR')
def archivos():
    # Aquí iría la lógica para obtener todos los archivos subidos para la empresa activa
    return render_template('contabilidad/archivos/index.html')

@descargas_bp.route('/archivos/subir', methods=['GET', 'POST'])
@login_required
@empresa_required
@permission_required('CONTADOR')
def subir_archivo():
    if request.method == 'POST':
        # Aquí iría la lógica para subir un nuevo archivo
        flash('Archivo subido correctamente', 'success')
        return redirect(url_for('descargas.archivos'))
    return render_template('contabilidad/archivos/upload.html')

@descargas_bp.route('/archivos/eliminar/<int:id>')
@login_required
@empresa_required
@permission_required('CONTADOR')
def eliminar_archivo(id):
    # Aquí iría la lógica para eliminar un archivo
    flash('Archivo eliminado correctamente', 'success')
    return redirect(url_for('descargas.archivos'))