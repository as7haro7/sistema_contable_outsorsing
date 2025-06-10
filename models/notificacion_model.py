from models.database import db_manager
from datetime import datetime

class NotificacionModel:
    @staticmethod
    def get_user_notifications(user_id, limit=5):
        """Obtener notificaciones del usuario"""
        connection = db_manager.get_master_connection()
        
        query = """
            SELECT id, titulo, mensaje, tipo, fecha_creacion, leida
            FROM notificaciones
            WHERE usuario_id = %s
            ORDER BY fecha_creacion DESC
            LIMIT %s
        """
        
        return db_manager.execute_query(connection, query, (user_id, limit))
    
    @staticmethod
    def get_unread_count(user_id):
        """Obtener cantidad de notificaciones no leídas"""
        connection = db_manager.get_master_connection()
        
        query = """
            SELECT COUNT(*) as count
            FROM notificaciones
            WHERE usuario_id = %s AND leida = FALSE
        """
        
        result = db_manager.execute_query(connection, query, (user_id,))
        return result[0]['count'] if result else 0
    
    @staticmethod
    def mark_as_read(notification_id):
        """Marcar notificación como leída"""
        connection = db_manager.get_master_connection()
        
        query = """
            UPDATE notificaciones
            SET leida = TRUE
            WHERE id = %s
        """
        
        return db_manager.execute_query(connection, query, (notification_id,), fetch=False)
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Marcar todas las notificaciones del usuario como leídas"""
        connection = db_manager.get_master_connection()
        
        query = """
            UPDATE notificaciones
            SET leida = TRUE
            WHERE usuario_id = %s
        """
        
        return db_manager.execute_query(connection, query, (user_id,), fetch=False)
    
    @staticmethod
    def create_notification(user_id, titulo, mensaje, tipo='info'):
        """Crear una nueva notificación"""
        connection = db_manager.get_master_connection()
        
        query = """
            INSERT INTO notificaciones (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
            VALUES (%s, %s, %s, %s, %s, FALSE)
            RETURNING id
        """
        
        result = db_manager.execute_query(
            connection, 
            query, 
            (user_id, titulo, mensaje, tipo, datetime.now())
        )
        
        return result[0]['id'] if result else None