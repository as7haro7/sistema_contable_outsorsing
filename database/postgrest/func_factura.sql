-- === FUNCIONES Y PROCEDIMIENTOS PARA GESTIÓN DE FACTURAS ===

-- === FUNCIÓN PARA CALCULAR IVA Y VALORES ===
CREATE OR REPLACE FUNCTION calcular_valores_factura(
    p_importe NUMERIC,
    p_exento NUMERIC DEFAULT 0,
    p_ice NUMERIC DEFAULT 0,
    p_tasa_iva NUMERIC DEFAULT 0.13
)
RETURNS TABLE(
    neto NUMERIC,
    iva NUMERIC,
    total_calculado NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (p_importe - COALESCE(p_exento, 0) - COALESCE(p_ice, 0)) as neto,
        ROUND((p_importe - COALESCE(p_exento, 0) - COALESCE(p_ice, 0)) * p_tasa_iva, 2) as iva,
        p_importe as total_calculado;
END;
$$ LANGUAGE plpgsql;

-- === FUNCIÓN PARA VALIDAR FECHAS DE FACTURAS ===
CREATE OR REPLACE FUNCTION validar_fecha_factura(p_fecha DATE)
RETURNS TEXT AS $$
BEGIN
    -- No puede ser fecha futura
    IF p_fecha > CURRENT_DATE THEN
        RETURN 'La fecha de la factura no puede ser futura';
    END IF;
    
    -- No puede ser muy antigua (más de 2 años)
    IF p_fecha < (CURRENT_DATE - INTERVAL '2 years') THEN
        RETURN 'La fecha de la factura es muy antigua';
    END IF;
    
    -- Validar que no sea fin de semana para facturas comerciales (opcional)
    -- IF EXTRACT(dow FROM p_fecha) IN (0, 6) THEN
    --     RETURN 'No se pueden registrar facturas en fines de semana';
    -- END IF;
    
    RETURN 'OK';
END;
$$ LANGUAGE plpgsql;

-- === FUNCIÓN PARA VERIFICAR DUPLICADOS DE COMPRAS ===
CREATE OR REPLACE FUNCTION existe_compra_duplicada(
    p_nit VARCHAR,
    p_factura VARCHAR,
    p_fecha DATE,
    p_proveedor INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    count_duplicados INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO count_duplicados
    FROM LibroCompras
    WHERE nit = p_nit 
      AND factura = p_factura 
      AND fecha = p_fecha
      AND proveedor = p_proveedor
      AND estado != 'ANULADO';
    
    RETURN count_duplicados > 0;
END;
$$ LANGUAGE plpgsql;

-- === FUNCIÓN PARA VERIFICAR DUPLICADOS DE VENTAS ===
CREATE OR REPLACE FUNCTION existe_venta_duplicada(
    p_nit VARCHAR,
    p_factura VARCHAR,
    p_fecha DATE,
    p_cliente INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    count_duplicados INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO count_duplicados
    FROM LibroVentas
    WHERE nit = p_nit 
      AND factura = p_factura 
      AND fecha = p_fecha
      AND cliente = p_cliente
      AND estado != 'ANULADA';
    
    RETURN count_duplicados > 0;
END;
$$ LANGUAGE plpgsql;

-- === PROCEDIMIENTO PARA REGISTRAR COMPRA ===
CREATE OR REPLACE FUNCTION sp_registrar_compra(
    p_fecha DATE,
    p_nit VARCHAR,
    p_proveedor INTEGER,
    p_factura VARCHAR,
    p_autorizacion VARCHAR DEFAULT NULL,
    p_codigocontrol VARCHAR DEFAULT NULL,
    p_importe NUMERIC,
    p_exento NUMERIC DEFAULT 0,
    p_ice NUMERIC DEFAULT 0,
    p_flete NUMERIC DEFAULT 0,
    p_tipo_fac VARCHAR DEFAULT 'FACTURA',
    p_usuario VARCHAR DEFAULT 'sistema'
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    factura_id INTEGER,
    valores_calculados JSON
) AS $$
DECLARE
    v_error_msg TEXT;
    v_neto NUMERIC;
    v_iva NUMERIC;
    v_total NUMERIC;
    v_new_id INTEGER;
    v_proveedor_existe BOOLEAN;
BEGIN
    -- Validar fecha
    SELECT validar_fecha_factura(p_fecha) INTO v_error_msg;
    IF v_error_msg != 'OK' THEN
        RETURN QUERY SELECT FALSE, v_error_msg, NULL::INTEGER, NULL::JSON;
        RETURN;
    END IF;
    
    -- Verificar que existe el proveedor
    SELECT EXISTS(SELECT 1 FROM proveedor WHERE id = p_proveedor AND activo = TRUE) INTO v_proveedor_existe;
    IF NOT v_proveedor_existe THEN
        RETURN QUERY SELECT FALSE, 'El proveedor especificado no existe o está inactivo', NULL::INTEGER, NULL::JSON;
        RETURN;
    END IF;
    
    -- Verificar duplicados
    IF existe_compra_duplicada(p_nit, p_factura, p_fecha, p_proveedor) THEN
        RETURN QUERY SELECT FALSE, 'Ya existe una compra con esos datos', NULL::INTEGER, NULL::JSON;
        RETURN;
    END IF;
    
    -- Calcular valores
    SELECT c.neto, c.iva, c.total_calculado 
    INTO v_neto, v_iva, v_total
    FROM calcular_valores_factura(p_importe, p_exento, p_ice) c;
    
    -- Insertar registro
    INSERT INTO LibroCompras (
        tipo_fac, fecha, nit, proveedor, factura, autorizacion, codigocontrol,
        importe, exento, ice, neto, iva, flete, usuario, fechasys
    ) VALUES (
        p_tipo_fac, p_fecha, p_nit, p_proveedor, p_factura, p_autorizacion, p_codigocontrol,
        p_importe, p_exento, p_ice, v_neto, v_iva, p_flete, p_usuario, CURRENT_TIMESTAMP
    ) RETURNING id INTO v_new_id;
    
    -- Retornar resultado exitoso
    RETURN QUERY SELECT 
        TRUE,
        'Compra registrada exitosamente'::TEXT,
        v_new_id,
        json_build_object(
            'neto', v_neto,
            'iva', v_iva,
            'total', v_total,
            'exento', p_exento,
            'ice', p_ice,
            'flete', p_flete
        );
        
EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT FALSE, 'Error interno: ' || SQLERRM, NULL::INTEGER, NULL::JSON;
END;
$$ LANGUAGE plpgsql;

-- === PROCEDIMIENTO PARA REGISTRAR VENTA ===
CREATE OR REPLACE FUNCTION sp_registrar_venta(
    p_fecha DATE,
    p_nit VARCHAR,
    p_cliente INTEGER,
    p_razonsocial VARCHAR,
    p_factura VARCHAR,
    p_autorizacion VARCHAR,
    p_importe NUMERIC,
    p_exento NUMERIC DEFAULT 0,
    p_ice NUMERIC DEFAULT 0,
    p_usuario VARCHAR DEFAULT 'sistema'
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    factura_id INTEGER,
    valores_calculados JSON
) AS $$
DECLARE
    v_error_msg TEXT;
    v_neto NUMERIC;
    v_iva NUMERIC;
    v_total NUMERIC;
    v_new_id INTEGER;
    v_cliente_existe BOOLEAN;
BEGIN
    -- Validar fecha
    SELECT validar_fecha_factura(p_fecha) INTO v_error_msg;
    IF v_error_msg != 'OK' THEN
        RETURN QUERY SELECT FALSE, v_error_msg, NULL::INTEGER, NULL::JSON;
        RETURN;
    END IF;
    
    -- Verificar que existe el cliente
    SELECT EXISTS(SELECT 1 FROM cliente WHERE id = p_cliente AND activo = TRUE) INTO v_cliente_existe;
    IF NOT v_cliente_existe THEN
        RETURN QUERY SELECT FALSE, 'El cliente especificado no existe o está inactivo', NULL::INTEGER, NULL::JSON;
        RETURN;
    END IF;
    
    -- Verificar duplicados
    IF existe_venta_duplicada(p_nit, p_factura, p_fecha, p_cliente) THEN
        RETURN QUERY SELECT FALSE, 'Ya existe una venta con esos datos', NULL::INTEGER, NULL::JSON;
        RETURN;
    END IF;
    
    -- Calcular valores
    SELECT c.neto, c.iva, c.total_calculado 
    INTO v_neto, v_iva, v_total
    FROM calcular_valores_factura(p_importe, p_exento, p_ice) c;
    
    -- Insertar registro
    INSERT INTO LibroVentas (
        fecha, nit, cliente, razonsocial, factura, autorizacion,
        importe, exento, ice, neto, iva, usuario, fechasys
    ) VALUES (
        p_fecha, p_nit, p_cliente, p_razonsocial, p_factura, p_autorizacion,
        p_importe, p_exento, p_ice, v_neto, v_iva, p_usuario, CURRENT_TIMESTAMP
    ) RETURNING id INTO v_new_id;
    
    -- Retornar resultado exitoso
    RETURN QUERY SELECT 
        TRUE,
        'Venta registrada exitosamente'::TEXT,
        v_new_id,
        json_build_object(
            'neto', v_neto,
            'iva', v_iva,
            'total', v_total,
            'exento', p_exento,
            'ice', p_ice
        );
        
EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT FALSE, 'Error interno: ' || SQLERRM, NULL::INTEGER, NULL::JSON;
END;
$$ LANGUAGE plpgsql;

-- === FUNCIÓN PARA ANULAR FACTURAS ===
CREATE OR REPLACE FUNCTION sp_anular_compra(
    p_id INTEGER,
    p_motivo VARCHAR DEFAULT 'Anulación manual',
    p_usuario VARCHAR DEFAULT 'sistema'
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    v_existe BOOLEAN;
    v_estado_actual VARCHAR;
BEGIN
    -- Verificar que existe la compra
    SELECT EXISTS(SELECT 1 FROM LibroCompras WHERE id = p_id), 
           estado
    INTO v_existe, v_estado_actual
    FROM LibroCompras WHERE id = p_id;
    
    IF NOT v_existe THEN
        RETURN QUERY SELECT FALSE, 'La factura de compra no existe';
        RETURN;
    END IF;
    
    IF v_estado_actual = 'ANULADO' THEN
        RETURN QUERY SELECT FALSE, 'La factura ya está anulada';
        RETURN;
    END IF;
    
    -- Anular la factura
    UPDATE LibroCompras 
    SET estado = 'ANULADO',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id = p_id;
    
    RETURN QUERY SELECT TRUE, 'Factura de compra anulada exitosamente';
        
EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT FALSE, 'Error al anular: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_anular_venta(
    p_id INTEGER,
    p_motivo VARCHAR DEFAULT 'Anulación manual',
    p_usuario VARCHAR DEFAULT 'sistema'
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    v_existe BOOLEAN;
    v_estado_actual VARCHAR;
BEGIN
    -- Verificar que existe la venta
    SELECT EXISTS(SELECT 1 FROM LibroVentas WHERE id = p_id), 
           estado
    INTO v_existe, v_estado_actual
    FROM LibroVentas WHERE id = p_id;
    
    IF NOT v_existe THEN
        RETURN QUERY SELECT FALSE, 'La factura de venta no existe';
        RETURN;
    END IF;
    
    IF v_estado_actual = 'ANULADA' THEN
        RETURN QUERY SELECT FALSE, 'La factura ya está anulada';
        RETURN;
    END IF;
    
    -- Anular la factura
    UPDATE LibroVentas 
    SET estado = 'ANULADA',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id = p_id;
    
    RETURN QUERY SELECT TRUE, 'Factura de venta anulada exitosamente';
        
EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT FALSE, 'Error al anular: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- === VISTAS ADICIONALES PARA REPORTES ===

-- Vista de resumen de compras por período
CREATE OR REPLACE VIEW v_resumen_compras_periodo AS
SELECT 
    DATE_TRUNC('month', fecha) as periodo,
    COUNT(*) as total_facturas,
    COUNT(CASE WHEN estado = 'PENDIENTE' THEN 1 END) as pendientes,
    COUNT(CASE WHEN estado = 'CONTABILIZADO' THEN 1 END) as contabilizadas,
    COUNT(CASE WHEN estado = 'ANULADO' THEN 1 END) as anuladas,
    SUM(CASE WHEN estado != 'ANULADO' THEN importe ELSE 0 END) as total_importe,
    SUM(CASE WHEN estado != 'ANULADO' THEN iva ELSE 0 END) as total_iva,
    SUM(CASE WHEN estado != 'ANULADO' THEN neto ELSE 0 END) as total_neto
FROM LibroCompras
GROUP BY DATE_TRUNC('month', fecha)
ORDER BY periodo DESC;

-- Vista de resumen de ventas por período
CREATE OR REPLACE VIEW v_resumen_ventas_periodo AS
SELECT 
    DATE_TRUNC('month', fecha) as periodo,
    COUNT(*) as total_facturas,
    COUNT(CASE WHEN estado = 'EMITIDA' THEN 1 END) as emitidas,
    COUNT(CASE WHEN estado = 'COBRADA' THEN 1 END) as cobradas,
    COUNT(CASE WHEN estado = 'ANULADA' THEN 1 END) as anuladas,
    SUM(CASE WHEN estado != 'ANULADA' THEN importe ELSE 0 END) as total_importe,
    SUM(CASE WHEN estado != 'ANULADA' THEN iva ELSE 0 END) as total_iva,
    SUM(CASE WHEN estado != 'ANULADA' THEN neto ELSE 0 END) as total_neto
FROM LibroVentas
GROUP BY DATE_TRUNC('month', fecha)
ORDER BY periodo DESC;

-- Vista de facturas con problemas (para auditoría)
CREATE OR REPLACE VIEW v_facturas_problemas AS
-- Compras con problemas
SELECT 'COMPRA' as tipo, 
       id, 
       factura, 
       fecha, 
       nit,
       'IVA calculado incorrecto' as problema,
       importe, 
       iva, 
       (neto * 0.13) as iva_deberia_ser
FROM LibroCompras 
WHERE ABS(iva - ROUND(neto * 0.13, 2)) > 0.01 
  AND estado != 'ANULADO'

UNION ALL

-- Ventas con problemas  
SELECT 'VENTA' as tipo,
       id,
       factura,
       fecha,
       nit,
       'IVA calculado incorrecto' as problema,
       importe,
       iva,
       (neto * 0.13) as iva_deberia_ser
FROM LibroVentas 
WHERE ABS(iva - ROUND(neto * 0.13, 2)) > 0.01
  AND estado != 'ANULADA'

UNION ALL

-- Facturas con fechas futuras
SELECT 'COMPRA' as tipo,
       id,
       factura,
       fecha,
       nit,
       'Fecha futura' as problema,
       importe,
       iva,
       0 as iva_deberia_ser
FROM LibroCompras 
WHERE fecha > CURRENT_DATE

UNION ALL

SELECT 'VENTA' as tipo,
       id,
       factura,
       fecha,
       nit,
       'Fecha futura' as problema,
       importe,
       iva,
       0 as iva_deberia_ser
FROM LibroVentas 
WHERE fecha > CURRENT_DATE;

-- === FUNCIÓN PARA OBTENER ESTADÍSTICAS RÁPIDAS ===
CREATE OR REPLACE FUNCTION obtener_estadisticas_facturas(
    p_fecha_desde DATE DEFAULT NULL,
    p_fecha_hasta DATE DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    v_fecha_desde DATE;
    v_fecha_hasta DATE;
    v_stats JSON;
BEGIN
    -- Establecer fechas por defecto (mes actual)
    v_fecha_desde := COALESCE(p_fecha_desde, DATE_TRUNC('month', CURRENT_DATE));
    v_fecha_hasta := COALESCE(p_fecha_hasta, CURRENT_DATE);
    
    SELECT json_build_object(
        'periodo', json_build_object(
            'desde', v_fecha_desde,
            'hasta', v_fecha_hasta
        ),
        'compras', json_build_object(
            'total_facturas', COUNT(CASE WHEN tipo = 'COMPRA' THEN 1 END),
            'total_importe', COALESCE(SUM(CASE WHEN tipo = 'COMPRA' THEN importe END), 0),
            'total_iva', COALESCE(SUM(CASE WHEN tipo = 'COMPRA' THEN iva END), 0)
        ),
        'ventas', json_build_object(
            'total_facturas', COUNT(CASE WHEN tipo = 'VENTA' THEN 1 END),
            'total_importe', COALESCE(SUM(CASE WHEN tipo = 'VENTA' THEN importe END), 0),
            'total_iva', COALESCE(SUM(CASE WHEN tipo = 'VENTA' THEN iva END), 0)
        )
    ) INTO v_stats
    FROM (
        SELECT 'COMPRA' as tipo, importe, iva FROM LibroCompras 
        WHERE fecha BETWEEN v_fecha_desde AND v_fecha_hasta AND estado != 'ANULADO'
        UNION ALL
        SELECT 'VENTA' as tipo, importe, iva FROM LibroVentas 
        WHERE fecha BETWEEN v_fecha_desde AND v_fecha_hasta AND estado != 'ANULADA'
    ) facturas;
    
    RETURN v_stats;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION validar_fecha_factura(p_fecha DATE)
RETURNS TEXT AS $$
BEGIN
    -- Ejemplo de validación
    IF p_fecha > CURRENT_DATE THEN
        RETURN 'La fecha no puede ser futura';
    END IF;
    RETURN 'OK';
END;
$$ LANGUAGE plpgsql;