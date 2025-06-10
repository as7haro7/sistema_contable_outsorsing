from models.database import db_manager
from datetime import datetime
import logging
import uuid
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import current_app
import subprocess
import os

class EmpresaModel:
    
    @staticmethod
    def crear_empresa(data):
        """
        Crea una nueva empresa y opcionalmente su base de datos contable asociada
        """
        conn = None
        try:
            conn = db_manager.get_master_connection()
            
            # Query para insertar empresa
            query = """
                INSERT INTO empresas (
                    razon_social, nit, representante_legal, telefono, celular, 
                    fax, email, website, pais, departamento, provincia, 
                    municipio, zona, direccion, codigo_postal, usuario_creacion
                ) VALUES (
                    %(razon_social)s, %(nit)s, %(representante_legal)s, %(telefono)s, 
                    %(celular)s, %(fax)s, %(email)s, %(website)s, %(pais)s, 
                    %(departamento)s, %(provincia)s, %(municipio)s, %(zona)s, 
                    %(direccion)s, %(codigo_postal)s, %(usuario_creacion)s
                ) RETURNING id, uuid
            """
            
            # Preparar parámetros con valores por defecto
            params = {
                'razon_social': data.get('razon_social'),
                'nit': data.get('nit'),
                'representante_legal': data.get('representante_legal'),
                'telefono': data.get('telefono'),
                'celular': data.get('celular'),
                'fax': data.get('fax'),
                'email': data.get('email'),
                'website': data.get('website'),
                'pais': data.get('pais', 'Bolivia'),
                'departamento': data.get('departamento'),
                'provincia': data.get('provincia'),
                'municipio': data.get('municipio'),
                'zona': data.get('zona'),
                'direccion': data.get('direccion'),
                'codigo_postal': data.get('codigo_postal'),
                'usuario_creacion': data.get('usuario_creacion', 'SYSTEM')
            }
            
            result = db_manager.execute_query(conn, query, params)
            empresa_id = result[0]['id']
            empresa_uuid = result[0]['uuid']
            
            # Crear la base de datos contable asociada si se solicita
            if data.get('crear_bd_contable', True):
                EmpresaModel.crear_estructura_contable(empresa_id)
            
            logging.info(f"Empresa creada exitosamente: ID {empresa_id}")
            return {
                'id': empresa_id,
                'uuid': empresa_uuid,
                'success': True,
                'message': 'Empresa creada exitosamente'
            }
            
        except Exception as e:
            logging.error(f"Error al crear empresa: {str(e)}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'message': f'Error al crear empresa: {str(e)}'
            }
        finally:
            if conn:
                conn.close()

    @staticmethod
    def listar_empresas(activo=None, limit=None, offset=0):
        """
        Lista las empresas con filtros opcionales
        """
        conn = None
        try:
            conn = db_manager.get_master_connection()
            
            # Query base
            query = """
                SELECT 
                    id, uuid, razon_social, nit, representante_legal,
                    telefono, celular, email, website, pais, departamento,
                    provincia, municipio, zona, direccion, activo,
                    fecha_registro, fecha_actualizacion
                FROM empresas
            """
            
            # Construir WHERE dinámico
            where_conditions = []
            params = {}
            
            if activo is not None:
                where_conditions.append("activo = %(activo)s")
                params['activo'] = activo
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            
            # Ordenar por fecha de registro
            query += " ORDER BY fecha_registro DESC"
            
            # Agregar paginación si se especifica
            if limit:
                query += " LIMIT %(limit)s OFFSET %(offset)s"
                params['limit'] = limit
                params['offset'] = offset
            
            result = db_manager.execute_query(conn, query, params)
            return result
            
        except Exception as e:
            logging.error(f"Error al listar empresas: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_empresa_por_id(empresa_id):
        """
        Obtiene una empresa específica por su ID
        """
        try:
            conn = db_manager.get_master_connection()
            
            query = """
                SELECT 
                    id, uuid, razon_social, nit, representante_legal,
                    telefono, celular, fax, email, website, pais, 
                    departamento, provincia, municipio, zona, direccion,
                    codigo_postal, activo, fecha_registro, fecha_actualizacion,
                    usuario_creacion, usuario_actualizacion
                FROM empresas 
                WHERE id = %(empresa_id)s
            """
            
            result = db_manager.execute_query(conn, query, {'empresa_id': empresa_id})
            return result[0] if result else None
            
        except Exception as e:
            logging.error(f"Error al obtener empresa: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_empresa_por_nit(nit):
        """
        Obtiene una empresa por su NIT
        """
        try:
            conn = db_manager.get_master_connection()
            
            query = """
                SELECT 
                    id, uuid, razon_social, nit, representante_legal,
                    telefono, celular, email, activo
                FROM empresas 
                WHERE nit = %(nit)s
            """
            
            result = db_manager.execute_query(conn, query, {'nit': nit})
            return result[0] if result else None
            
        except Exception as e:
            logging.error(f"Error al obtener empresa por NIT: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def actualizar_empresa(empresa_id, data):
        """
        Actualiza los datos de una empresa existente
        """
        conn = None
        try:
            conn = db_manager.get_master_connection()
            
            # Construir query dinámico basado en los campos proporcionados
            campos_actualizables = [
                'razon_social', 'nit', 'representante_legal', 'telefono', 
                'celular', 'fax', 'email', 'website', 'pais', 'departamento',
                'provincia', 'municipio', 'zona', 'direccion', 'codigo_postal'
            ]
            
            set_clauses = []
            params = {'empresa_id': empresa_id}
            
            for campo in campos_actualizables:
                if campo in data:
                    set_clauses.append(f"{campo} = %({campo})s")
                    params[campo] = data[campo]
            
            if not set_clauses:
                return {
                    'success': False,
                    'message': 'No hay campos para actualizar'
                }
            
            # Agregar campos de auditoría
            set_clauses.append("fecha_actualizacion = CURRENT_TIMESTAMP")
            if 'usuario_actualizacion' in data:
                set_clauses.append("usuario_actualizacion = %(usuario_actualizacion)s")
                params['usuario_actualizacion'] = data['usuario_actualizacion']
            
            query = f"""
                UPDATE empresas 
                SET {', '.join(set_clauses)}
                WHERE id = %(empresa_id)s
                RETURNING id
            """
            
            result = db_manager.execute_query(conn, query, params)
            
            if result:
                return {
                    'success': True,
                    'message': 'Empresa actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Empresa no encontrada'
                }
                
        except Exception as e:
            logging.error(f"Error al actualizar empresa: {str(e)}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'message': f'Error al actualizar empresa: {str(e)}'
            }
        finally:
            if conn:
                conn.close()

    @staticmethod
    def eliminar_empresa(empresa_id, usuario_eliminacion=None):
        """
        Desactiva una empresa (soft delete)
        """
        conn = None
        try:
            conn = db_manager.get_master_connection()
            
            query = """
                UPDATE empresas 
                SET 
                    activo = FALSE,
                    fecha_actualizacion = CURRENT_TIMESTAMP,
                    usuario_actualizacion = %(usuario_actualizacion)s
                WHERE id = %(empresa_id)s
                RETURNING id
            """
            
            params = {
                'empresa_id': empresa_id,
                'usuario_actualizacion': usuario_eliminacion or 'SYSTEM'
            }
            
            result = db_manager.execute_query(conn, query, params)
            
            if result:
                return {
                    'success': True,
                    'message': 'Empresa desactivada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Empresa no encontrada'
                }
                
        except Exception as e:
            logging.error(f"Error al eliminar empresa: {str(e)}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'message': f'Error al eliminar empresa: {str(e)}'
            }
        finally:
            if conn:
                conn.close()

    @staticmethod
    def eliminar_empresa_definitivo(empresa_id):
        """
        Elimina definitivamente una empresa (hard delete)
        Solo usar en casos especiales y con mucho cuidado
        """
        conn = None
        try:
            conn = db_manager.get_master_connection()
            
            # Primero verificar que no tenga gestiones asociadas
            check_query = "SELECT COUNT(*) as count FROM gestiones WHERE empresa_id = %(empresa_id)s"
            check_result = db_manager.execute_query(conn, check_query, {'empresa_id': empresa_id})
            
            if check_result[0]['count'] > 0:
                return {
                    'success': False,
                    'message': 'No se puede eliminar: la empresa tiene gestiones asociadas'
                }
            
            query = "DELETE FROM empresas WHERE id = %(empresa_id)s RETURNING id"
            result = db_manager.execute_query(conn, query, {'empresa_id': empresa_id})
            
            if result:
                return {
                    'success': True,
                    'message': 'Empresa eliminada definitivamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Empresa no encontrada'
                }
                
        except Exception as e:
            logging.error(f"Error al eliminar empresa definitivamente: {str(e)}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'message': f'Error al eliminar empresa: {str(e)}'
            }
        finally:
            if conn:
                conn.close()

    @staticmethod
    def buscar_empresas(termino_busqueda):
        """
        Busca empresas por razón social, NIT o representante legal
        """
        try:
            conn = db_manager.get_master_connection()
            
            query = """
                SELECT 
                    id, uuid, razon_social, nit, representante_legal,
                    telefono, email, activo
                FROM empresas 
                WHERE 
                    (razon_social ILIKE %(termino)s OR 
                     nit ILIKE %(termino)s OR 
                     representante_legal ILIKE %(termino)s) AND
                    activo = TRUE
                ORDER BY razon_social
            """
            
            termino_like = f"%{termino_busqueda}%"
            result = db_manager.execute_query(conn, query, {'termino': termino_like})
            return result
            
        except Exception as e:
            logging.error(f"Error al buscar empresas: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_estadisticas_empresa():
        """
        Obtiene estadísticas generales de las empresas
        """
        conn = None  # <-- Agrega esto
        try:
            conn = db_manager.get_master_connection()
            
            query = """
                SELECT 
                    COUNT(*) as total_empresas,
                    COUNT(CASE WHEN activo = TRUE THEN 1 END) as empresas_activas,
                    COUNT(CASE WHEN activo = FALSE THEN 1 END) as empresas_inactivas,
                    COUNT(CASE WHEN fecha_registro >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as nuevas_ultimo_mes
                FROM empresas
            """
            
            result = db_manager.execute_query(conn, query)
            return result[0] if result else {}
            
        except Exception as e:
            logging.error(f"Error al obtener estadísticas: {str(e)}")
            return {}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def crear_estructura_contable(empresa_id):
        """
        Crea la base de datos contable y restaura la estructura desde un backup (.backup).
        Usa el backup más reciente de la empresa si existe, si no el backup base.
        """
        conn = None
        try:
            db_name = f"{current_app.config['COMPANY_DB_PREFIX']}{empresa_id}"

            # Crear la base de datos si no existe
            conn = psycopg2.connect(
                host=current_app.config['MASTER_DB_HOST'],
                port=current_app.config['MASTER_DB_PORT'],
                dbname=current_app.config['MASTER_DB_NAME'],
                user=current_app.config['MASTER_DB_USER'],
                password=current_app.config['MASTER_DB_PASSWORD']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                if not cursor.fetchone():
                    cursor.execute(f'CREATE DATABASE "{db_name}"')

            # Buscar backup personalizado o usar el base
            backup_dir = 'backups'
            backup_path = 'database/db_contab.backup'
            if os.path.isdir(backup_dir):
                archivos = [f for f in os.listdir(backup_dir) if f.startswith(db_name) and f.endswith('.backup')]
                if archivos:
                    archivos.sort(reverse=True)
                    backup_path = os.path.join(backup_dir, archivos[0])

            # Restaurar el backup usando pg_restore
            comando = [
                r'C:\Program Files\PostgreSQL\17\bin\pg_restore.exe',  # Ajusta la ruta si es necesario
                '--username', current_app.config['MASTER_DB_USER'],
                '--host', current_app.config['MASTER_DB_HOST'],
                '--port', str(current_app.config['MASTER_DB_PORT']),
                '--dbname', db_name,
                '--no-owner',
                backup_path
            ]
            env = {**os.environ, 'PGPASSWORD': current_app.config['MASTER_DB_PASSWORD']}
            resultado = subprocess.run(comando, capture_output=True, text=True, env=env)

            # Guardar logs
            with open('log_restore_pg.txt', 'w') as log_file:
                log_file.write("=== STDOUT ===\n")
                log_file.write(resultado.stdout)
                log_file.write("\n\n=== STDERR ===\n")
                log_file.write(resultado.stderr)

            if resultado.returncode != 0:
                return {'success': False, 'message': f'Error al restaurar backup: {resultado.stderr}'}
            return {'success': True, 'message': 'Base de datos y estructura contable restauradas correctamente'}

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            if conn:
                conn.close()


    @staticmethod
    def validar_nit_unico(nit, empresa_id=None):
        """
        Valida que el NIT sea único en el sistema
        """
        conn = None  # <-- Agrega esto
        try:
            conn = db_manager.get_master_connection()
            
            query = "SELECT id FROM empresas WHERE nit = %(nit)s"
            params = {'nit': nit}
            
            if empresa_id:
                query += " AND id != %(empresa_id)s"
                params['empresa_id'] = empresa_id
            
            result = db_manager.execute_query(conn, query, params)
            return len(result) == 0  # True si es único
            
        except Exception as e:
            logging.error(f"Error al validar NIT: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()


    @staticmethod
    def activar_empresa(empresa_id, usuario_activacion=None):
        """
        Reactiva una empresa (soft undelete)
        """
        conn = None
        try:
            conn = db_manager.get_master_connection()
            query = """
                UPDATE empresas
                SET activo = TRUE,
                    fecha_actualizacion = CURRENT_TIMESTAMP,
                    usuario_actualizacion = %(usuario_actualizacion)s
                WHERE id = %(empresa_id)s
                RETURNING id
            """
            params = {
                'empresa_id': empresa_id,
                'usuario_actualizacion': usuario_activacion or 'SYSTEM'
            }
            result = db_manager.execute_query(conn, query, params)
            if result:
                return {'success': True, 'message': 'Empresa reactivada exitosamente'}
            else:
                return {'success': False, 'message': 'Empresa no encontrada'}
        except Exception as e:
            logging.error(f"Error al reactivar empresa: {str(e)}")
            if conn:
                conn.rollback()
            return {'success': False, 'message': f'Error al reactivar empresa: {str(e)}'}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def backup_contabilidad(empresa_id):
        """
        Realiza un backup de la base contable de la empresa usando pg_dump.
        """
        db_name = f"{current_app.config['COMPANY_DB_PREFIX']}{empresa_id}"
        fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join('backups')
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"{db_name}_{fecha}.backup")

        comando = [
            r'C:\Program Files\PostgreSQL\17\bin\pg_dump.exe',  # Ruta completa aquí
            '-U', current_app.config['MASTER_DB_USER'],
            '-h', current_app.config['MASTER_DB_HOST'],
            '-p', str(current_app.config['MASTER_DB_PORT']),
            '-F', 'c',
            '-f', backup_path,
            db_name
        ]
        env = {
            **os.environ,
            'PGPASSWORD': current_app.config['MASTER_DB_PASSWORD']
        }
        resultado = subprocess.run(comando, capture_output=True, text=True, env=env)
        if resultado.returncode != 0:
            return {'success': False, 'message': f'Error al hacer backup: {resultado.stderr}'}
        return {'success': True, 'message': f'Backup creado: {backup_path}', 'backup_path': backup_path}