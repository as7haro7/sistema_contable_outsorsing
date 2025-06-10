from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.notificacion_model import NotificacionModel
from utils.decorators import login_required

notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/notificaciones')
@login_required
def listar():
    """Mostrar todas las notificaciones del usuario"""
    user_id = session.get('user_id')
    notificaciones = NotificacionModel.get_user_notifications(user_id, limit=50)
    return render_template('notificaciones/index.html', notificaciones=notificaciones)

@notificaciones_bp.route('/notificaciones/api/get')
@login_required
def get_notificaciones():
    """API para obtener notificaciones recientes"""
    user_id = session.get('user_id')
    notificaciones = NotificacionModel.get_user_notifications(user_id)
    count = NotificacionModel.get_unread_count(user_id)
    
    return jsonify({
        'notificaciones': notificaciones,
        'count': count
    })

@notificaciones_bp.route('/notificaciones/marcar-leida/<int:notificacion_id>', methods=['POST'])
@login_required
def marcar_leida(notificacion_id):
    """Marcar una notificación como leída"""
    NotificacionModel.mark_as_read(notificacion_id)
    return jsonify({'success': True})

@notificaciones_bp.route('/notificaciones/marcar-todas-leidas', methods=['POST'])
@login_required
def marcar_todas_leidas():
    """Marcar todas las notificaciones como leídas"""
    user_id = session.get('user_id')
    NotificacionModel.mark_all_as_read(user_id)
    return jsonify({'success': True})