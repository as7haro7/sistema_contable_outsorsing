import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-muy-segura'
    
    # Base de datos maestra
    MASTER_DB_HOST =  'localhost'
    MASTER_DB_PORT =  5432
    # MASTER_DB_NAME =  'gestion_empresarial'
    # MASTER_DB_NAME =  'gestion_emp'
    MASTER_DB_NAME =  'restauracion_gestion_empresarial'
    MASTER_DB_USER =  'postgres'
    MASTER_DB_PASSWORD =  '123456'
    
    # Configuración empresa
    # COMPANY_DB_PREFIX = 'BD_CONTABILIDAD_EMPRESA_'
    COMPANY_DB_PREFIX = 'contabilidad_emp_'
    
    # Uploads
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Paginación
    ITEMS_PER_PAGE = 20
    
    # Sesiones
    SESSION_TIMEOUT = 3600  # 1 hora