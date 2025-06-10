-- =====================================================
-- BASE DE DATOS MEJORADA PARA OUTSOURCING CONTABLE
-- =====================================================

-- Habilitar extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- === EMPRESAS Y GESTIÓN ===

CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nit VARCHAR(20) UNIQUE NOT NULL,
    representante_legal VARCHAR(255),
    telefono VARCHAR(20),
    celular VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    pais VARCHAR(100) DEFAULT 'Bolivia',
    departamento VARCHAR(100),
    provincia VARCHAR(100),
    municipio VARCHAR(100),
    zona VARCHAR(100),
    direccion TEXT,
    codigo_postal VARCHAR(10),
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(100),
    usuario_actualizacion VARCHAR(100),
    
    CONSTRAINT chk_nit_formato CHECK (nit ~ '^[0-9]{7,12}$'),
    CONSTRAINT chk_email_formato CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE TABLE gestiones (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    empresa_id INTEGER NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    periodo VARCHAR(4) NOT NULL, -- Año de gestión
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    nombre_base_datos VARCHAR(100),
    codigo_moneda CHAR(3) DEFAULT 'BOB', -- ISO 4217
    nombre_moneda VARCHAR(50) DEFAULT 'Boliviano',
    activo BOOLEAN DEFAULT TRUE,
    cerrada BOOLEAN DEFAULT FALSE,
    fecha_cierre TIMESTAMP WITH TIME ZONE,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(100),
    usuario_actualizacion VARCHAR(100),
    
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
    
    CONSTRAINT chk_periodo_formato CHECK (periodo ~ '^[0-9]{4}$'),
    CONSTRAINT chk_fechas_coherentes CHECK (fecha_inicio < fecha_fin),
    CONSTRAINT chk_moneda_iso CHECK (codigo_moneda ~ '^[A-Z]{3}$'),
    CONSTRAINT uk_empresa_periodo UNIQUE (empresa_id, periodo)
);

-- === USUARIOS Y AUTENTICACIÓN ===

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    es_super_usuario BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    requiere_cambio_password BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMP WITH TIME ZONE,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado_hasta TIMESTAMP WITH TIME ZONE,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    supervisor_id INTEGER,
    
    FOREIGN KEY (supervisor_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_username_formato CHECK (username ~ '^[a-zA-Z0-9_]{3,50}$'),
    CONSTRAINT chk_email_formato CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_intentos_fallidos CHECK (intentos_fallidos >= 0 AND intentos_fallidos <= 10)
);

-- Relación usuarios-empresas (muchos a muchos)
CREATE TABLE usuario_empresas (
    usuario_id INTEGER,
    empresa_id INTEGER,
    rol VARCHAR(50) DEFAULT 'CONTADOR',
    activo BOOLEAN DEFAULT TRUE,
    fecha_asignacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_revocacion TIMESTAMP WITH TIME ZONE,
    asignado_por INTEGER,
    
    PRIMARY KEY (usuario_id, empresa_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
    FOREIGN KEY (asignado_por) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_rol_valido CHECK (rol IN ('ADMIN', 'CONTADOR', 'ASISTENTE', 'CONSULTOR'))
);

-- Relación usuarios-gestiones específicas
CREATE TABLE usuario_gestiones (
    usuario_id INTEGER,
    gestion_id INTEGER,
    nivel_acceso VARCHAR(20) DEFAULT 'LECTURA',
    activo BOOLEAN DEFAULT TRUE,
    fecha_asignacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_revocacion TIMESTAMP WITH TIME ZONE,
    asignado_por INTEGER,
    
    PRIMARY KEY (usuario_id, gestion_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (gestion_id) REFERENCES gestiones(id) ON DELETE CASCADE,
    FOREIGN KEY (asignado_por) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_nivel_acceso CHECK (nivel_acceso IN ('LECTURA', 'ESCRITURA', 'ADMINISTRADOR'))
);

-- === SESIONES Y SEGURIDAD ===

CREATE TABLE sesiones (
    id SERIAL PRIMARY KEY,
    token_sesion VARCHAR(255) UNIQUE NOT NULL,
    usuario_id INTEGER NOT NULL,
    ip_address INET,
    user_agent TEXT,
    navegador VARCHAR(100),
    version_navegador VARCHAR(50),
    plataforma VARCHAR(100),
    dispositivo VARCHAR(100),
    fecha_inicio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_ultimo_acceso TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE,
    empresa_contexto INTEGER,
    gestion_contexto INTEGER,
    datos_sesion JSONB,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (empresa_contexto) REFERENCES empresas(id) ON DELETE SET NULL,
    FOREIGN KEY (gestion_contexto) REFERENCES gestiones(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_expiracion_futura CHECK (fecha_expiracion > fecha_inicio)
);

-- === PERFILES Y PERMISOS ===

CREATE TABLE perfiles (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(100),
    ruta VARCHAR(255),
    icono VARCHAR(100),
    orden_menu INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    es_menu BOOLEAN DEFAULT FALSE,
    perfil_padre INTEGER,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(100),
    
    FOREIGN KEY (perfil_padre) REFERENCES perfiles(id) ON DELETE CASCADE,
    
    CONSTRAINT chk_codigo_formato CHECK (codigo ~ '^[A-Z0-9_]{2,50}$')
);

CREATE TABLE permisos_usuario (
    usuario_id INTEGER,
    perfil_id INTEGER,
    puede_crear BOOLEAN DEFAULT FALSE,
    puede_leer BOOLEAN DEFAULT TRUE,
    puede_actualizar BOOLEAN DEFAULT FALSE,
    puede_eliminar BOOLEAN DEFAULT FALSE,
    puede_imprimir BOOLEAN DEFAULT FALSE,
    puede_exportar BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_asignacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_revocacion TIMESTAMP WITH TIME ZONE,
    asignado_por INTEGER,
    
    PRIMARY KEY (usuario_id, perfil_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE,
    FOREIGN KEY (asignado_por) REFERENCES usuarios(id) ON DELETE SET NULL
);



-- === ÍNDICES PARA OPTIMIZACIÓN ===

-- Índices para empresas
CREATE INDEX idx_empresas_nit ON empresas(nit);
CREATE INDEX idx_empresas_activo ON empresas(activo);
CREATE INDEX idx_empresas_fecha_registro ON empresas(fecha_registro);

-- Índices para gestiones
CREATE INDEX idx_gestiones_empresa ON gestiones(empresa_id);
CREATE INDEX idx_gestiones_periodo ON gestiones(periodo);
CREATE INDEX idx_gestiones_activo ON gestiones(activo);

-- Índices para usuarios
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
CREATE INDEX idx_usuarios_ultimo_acceso ON usuarios(ultimo_acceso);

-- Índices para sesiones
CREATE INDEX idx_sesiones_usuario ON sesiones(usuario_id);
CREATE INDEX idx_sesiones_expiracion ON sesiones(fecha_expiracion);
CREATE INDEX idx_sesiones_activa ON sesiones(activa);
CREATE INDEX idx_sesiones_ip ON sesiones(ip_address);



-- === COMENTARIOS EN TABLAS ===

COMMENT ON TABLE empresas IS 'Empresas clientes del outsourcing contable';
COMMENT ON TABLE gestiones IS 'Gestiones/períodos contables por empresa';
COMMENT ON TABLE usuarios IS 'Usuarios del sistema de outsourcing';
COMMENT ON TABLE sesiones IS 'Sesiones activas de usuarios';
COMMENT ON TABLE perfiles IS 'Perfiles y menús del sistema';
COMMENT ON TABLE permisos_usuario IS 'Permisos específicos por usuario y perfil';


