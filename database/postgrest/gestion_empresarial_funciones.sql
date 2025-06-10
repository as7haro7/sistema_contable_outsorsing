-- =====================================================
--         CÓDIGO REVISADO Y OPTIMIZADO
-- =====================================================

-- === FUNCIONES DE UTILIDAD Y MANTENIMIENTO ===

-- Función para actualizar timestamp (Sin cambios, es correcta)
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers (Sin cambios, son correctos)
CREATE TRIGGER trg_empresas_actualizar_fecha BEFORE UPDATE ON empresas FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();
CREATE TRIGGER trg_gestiones_actualizar_fecha BEFORE UPDATE ON gestiones FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();
CREATE TRIGGER trg_usuarios_actualizar_fecha BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();


-- [OPTIMIZADO] Función de mantenimiento unificada. Reemplaza a limpiar_sesiones_expiradas y limpiar_datos_antiguos
-- NOTA: Se eliminó la referencia a la tabla 'auditoria' que no existe en el esquema.
CREATE OR REPLACE FUNCTION mantenimiento_limpiar_datos_antiguos()
RETURNS TEXT AS $$
DECLARE
    sesiones_eliminadas INTEGER;
    resultado TEXT;
BEGIN
    -- Limpia sesiones que expiraron hace más de 1 día para no afectar sesiones recién expiradas.
    DELETE FROM sesiones
    WHERE fecha_expiracion < (CURRENT_TIMESTAMP - INTERVAL '1 day');
    GET DIAGNOSTICS sesiones_eliminadas = ROW_COUNT;

    resultado := format('Limpieza completada: %s sesiones antiguas eliminadas.', sesiones_eliminadas);
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;


-- === VISTAS OPTIMIZADAS (CON JOINS IMPLÍCITOS) ===

-- [SIN CAMBIOS] Esta vista usa LEFT JOIN, que no tiene un equivalente implícito directo y funcional.
-- Se mantiene la sintaxis explícita para asegurar la correcta lógica de negocio.
CREATE OR REPLACE VIEW v_empresas_activas AS
SELECT
    e.id, e.uuid, e.razon_social, e.nit, e.representante_legal,
    e.telefono, e.email, e.direccion, e.departamento, e.municipio,
    COUNT(g.id) as total_gestiones,
    COUNT(CASE WHEN g.activo = TRUE THEN 1 END) as gestiones_activas
FROM empresas e
LEFT JOIN gestiones g ON e.id = g.empresa_id
WHERE e.activo = TRUE
GROUP BY e.id, e.uuid, e.razon_social, e.nit, e.representante_legal,
         e.telefono, e.email, e.direccion, e.departamento, e.municipio;

-- [RECOMENDACIÓN] Eliminar esta vista por redundancia con v_permisos_detallados
-- DROP VIEW IF EXISTS v_usuarios_permisos;

-- [OPTIMIZADO] Vista con joins implícitos
CREATE OR REPLACE VIEW v_usuarios_empresas AS
SELECT
    u.id as usuario_id, u.username, u.nombre_completo, u.email,
    u.activo as usuario_activo, e.id as empresa_id, e.razon_social,
    e.nit, ue.rol, ue.activo as asignacion_activa, ue.fecha_asignacion
FROM
    usuarios u, usuario_empresas ue, empresas e
WHERE
    u.id = ue.usuario_id
    AND ue.empresa_id = e.id
    AND u.activo = TRUE AND e.activo = TRUE;

-- [OPTIMIZADO] Vista con join implícito. LEFT JOIN se mantiene explícito.
CREATE OR REPLACE VIEW v_gestiones_completas AS
SELECT
    g.id as gestion_id, g.uuid as gestion_uuid, g.descripcion, g.periodo,
    g.fecha_inicio, g.fecha_fin, g.activo as gestion_activa, g.cerrada,
    e.id as empresa_id, e.razon_social, e.nit, e.representante_legal,
    COUNT(ug.usuario_id) as total_usuarios_asignados
FROM
    gestiones g
INNER JOIN empresas e ON g.empresa_id = e.id -- Explicit INNER JOIN
LEFT JOIN usuario_gestiones ug ON g.id = ug.gestion_id AND ug.activo = TRUE
WHERE
    e.activo = TRUE
GROUP BY g.id, g.uuid, g.descripcion, g.periodo, g.fecha_inicio, g.fecha_fin,
         g.activo, g.cerrada, e.id, e.razon_social, e.nit, e.representante_legal
ORDER BY g.periodo DESC, e.razon_social;

-- [OPTIMIZADO] Vista con joins implícitos. Reemplaza a la redundante v_usuarios_permisos.
CREATE OR REPLACE VIEW v_permisos_detallados AS
SELECT
    u.id as usuario_id, u.username, u.nombre_completo, p.id as perfil_id,
    p.codigo as perfil_codigo, p.nombre as perfil_nombre, p.modulo, p.ruta,
    pu.puede_crear, pu.puede_leer, pu.puede_actualizar, pu.puede_eliminar,
    pu.puede_imprimir, pu.puede_exportar, pu.activo as permiso_activo
FROM
    usuarios u, permisos_usuario pu, perfiles p
WHERE
    u.id = pu.usuario_id
    AND pu.perfil_id = p.id
    AND u.activo = TRUE AND p.activo = TRUE
ORDER BY u.username, p.orden_menu, p.nombre;

-- === FUNCIONES Y PROCEDIMIENTOS OPTIMIZADOS ===

-- [OPTIMIZADO] Función con join implícito. LEFT JOIN se mantiene explícito.
CREATE OR REPLACE FUNCTION obtener_empresas_usuario(p_usuario_id INTEGER)
RETURNS TABLE (
    empresa_id INTEGER,
    razon_social VARCHAR(255),
    nit VARCHAR(20),
    rol VARCHAR(50),
    total_gestiones BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id, e.razon_social, e.nit, ue.rol, COUNT(g.id) as total_gestiones
    FROM
        empresas e, usuario_empresas ue
    LEFT JOIN gestiones g ON e.id = g.empresa_id AND g.activo = TRUE
    WHERE
        e.id = ue.empresa_id
        AND ue.usuario_id = p_usuario_id
        AND ue.activo = TRUE
        AND e.activo = TRUE
    GROUP BY e.id, e.razon_social, e.nit, ue.rol
    ORDER BY e.razon_social;
END;
$$ LANGUAGE plpgsql;

-- [OPTIMIZADO] Función con join implícito.
CREATE OR REPLACE FUNCTION obtener_gestiones_usuario_empresa(
    p_usuario_id INTEGER,
    p_empresa_id INTEGER
)
RETURNS TABLE (
    gestion_id INTEGER,
    descripcion VARCHAR(255),
    periodo VARCHAR(4),
    fecha_inicio DATE,
    fecha_fin DATE,
    nivel_acceso VARCHAR(20),
    activa BOOLEAN,
    cerrada BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        g.id, g.descripcion, g.periodo, g.fecha_inicio, g.fecha_fin,
        ug.nivel_acceso, g.activo, g.cerrada
    FROM
        gestiones g, usuario_gestiones ug
    WHERE
        g.id = ug.gestion_id
        AND ug.usuario_id = p_usuario_id
        AND g.empresa_id = p_empresa_id
        AND ug.activo = TRUE
    ORDER BY g.periodo DESC;
END;
$$ LANGUAGE plpgsql;

-- [OPTIMIZADO] Función con join implícito.
CREATE OR REPLACE FUNCTION validar_permiso_usuario(
    p_usuario_id INTEGER,
    p_perfil_codigo VARCHAR(50),
    p_accion VARCHAR(20) -- 'crear', 'leer', 'actualizar', 'eliminar', 'imprimir', 'exportar'
)
RETURNS BOOLEAN AS $$
DECLARE
    tiene_permiso BOOLEAN := FALSE;
BEGIN
    SELECT
        CASE p_accion
            WHEN 'crear' THEN pu.puede_crear
            WHEN 'leer' THEN pu.puede_leer
            WHEN 'actualizar' THEN pu.puede_actualizar
            WHEN 'eliminar' THEN pu.puede_eliminar
            WHEN 'imprimir' THEN pu.puede_imprimir
            WHEN 'exportar' THEN pu.puede_exportar
            ELSE FALSE
        END INTO tiene_permiso
    FROM
        permisos_usuario pu, perfiles p
    WHERE
        pu.perfil_id = p.id
        AND pu.usuario_id = p_usuario_id
        AND p.codigo = p_perfil_codigo
        AND pu.activo = TRUE;

    RETURN COALESCE(tiene_permiso, FALSE);
END;
$$ LANGUAGE plpgsql;

