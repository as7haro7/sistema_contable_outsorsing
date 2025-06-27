CREATE OR REPLACE FUNCTION calcular_saldo_cuenta(p_cuenta VARCHAR)
RETURNS NUMERIC AS $$
DECLARE
    v_debe NUMERIC := 0;
    v_haber NUMERIC := 0;
    v_saldo NUMERIC := 0;
BEGIN
    -- suma movimientos debe
    SELECT COALESCE(SUM(ad.debebs), 0) INTO v_debe
    FROM Asiento_det ad
    JOIN Asiento a ON ad.cod_asiento = a.codigo
    WHERE ad.cuenta = p_cuenta AND a.estado = 'CONFIRMADO';

    -- suma movimientos haber
    SELECT COALESCE(SUM(ad.haberbs), 0) INTO v_haber
    FROM Asiento_det ad
    JOIN Asiento a ON ad.cod_asiento = a.codigo
    WHERE ad.cuenta = p_cuenta AND a.estado = 'CONFIRMADO';

    -- calculo saldo segun tipo de cuenta
    SELECT
        CASE
            WHEN pc.tipomov = 'DEUDOR' THEN (v_debe - v_haber)
            WHEN pc.tipomov = 'ACREEDOR' THEN (v_haber - v_debe)
            ELSE (v_debe - v_haber)
        END INTO v_saldo
    FROM Plancuenta pc
    WHERE pc.cuenta = p_cuenta;

    RETURN COALESCE(v_saldo, 0);
END;
$$ LANGUAGE plpgsql;



SELECT public.calcular_saldo_cuenta('110101');

--------------------------------------------------------------------------




DROP FUNCTION IF EXISTS balance_general(date, text, integer);

CREATE OR REPLACE FUNCTION balance_general(
    fecha_corte DATE,
    moneda TEXT,
)
RETURNS TABLE (
    cuenta VARCHAR(100),
    descrip VARCHAR(255),
    tipo_cuenta VARCHAR(50),
    nivel VARCHAR(50),
    saldo NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.cuenta,
        p.descrip,
        p.tipo_cuenta,
        p.nivel,
        CASE
            WHEN balance_general.moneda = 'BOB' THEN
                COALESCE(SUM(ad.debebs), 0) - COALESCE(SUM(ad.haberbs), 0)
            ELSE
                COALESCE(SUM(ad.debesus), 0) - COALESCE(SUM(ad.habersus), 0)
        END AS saldo
    FROM Plancuenta p
    LEFT JOIN Asiento_det ad ON p.cuenta = ad.cuenta
    LEFT JOIN Asiento a ON ad.cod_asiento = a.codigo
    WHERE p.tipo_cuenta IN ('ACTIVO', 'PASIVO', 'PATRIMONIO')
      AND p.activo = TRUE
      AND (a.fecha IS NULL OR (a.fecha <= fecha_corte AND a.estado = 'CONFIRMADO'))
    GROUP BY p.cuenta, p.descrip, p.tipo_cuenta, p.nivel
    ORDER BY p.cuenta;
END;
$$ LANGUAGE plpgsql;


SELECT * FROM balance_general('2024-12-31', 'BOB');



------ APARTE ----- 


-- sp 1
-- Generador simple de código de asiento 
CREATE OR REPLACE FUNCTION get_next_asiento_code(p_tipo VARCHAR, p_fecha DATE)
RETURNS VARCHAR AS $$
DECLARE
    v_codigo VARCHAR(50);
    v_count INT;
BEGIN
    SELECT COUNT(*)+1 INTO v_count FROM Asiento WHERE tipo = p_tipo AND fecha = p_fecha;
    v_codigo := p_tipo || TO_CHAR(p_fecha, 'YYYYMMDD') || '-' || LPAD(v_count::TEXT, 4, '0');
    RETURN v_codigo;
END;
$$ LANGUAGE plpgsql;

-- Procedimiento para crear asiento
CREATE OR REPLACE PROCEDURE sp_create_asiento(
    IN p_codigo VARCHAR(50),
    IN p_cta VARCHAR(100),
    IN p_tipo VARCHAR(50),
    IN p_secuencia INT,
    IN p_srs VARCHAR(50),
    IN p_glosa VARCHAR(500),
    IN p_fecha DATE,
    IN p_estado VARCHAR(20),
    IN p_usuario VARCHAR(50),
    IN p_detalles JSONB,
    OUT success BOOLEAN,
    OUT message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_debe_bs NUMERIC(18, 2) := 0;
    v_total_haber_bs NUMERIC(18, 2) := 0;
    v_total_debe_sus NUMERIC(18, 2) := 0;
    v_total_haber_sus NUMERIC(18, 2) := 0;
    det JSONB;
    v_cuenta_existe BOOLEAN;
    v_asiento_exists BOOLEAN;
    v_generated_codigo VARCHAR(50);
    i INT := 1;
BEGIN
    success := FALSE;
    message := '';

    -- Generar o usar código de asiento
    IF p_codigo IS NULL OR p_codigo = '' THEN
        SELECT get_next_asiento_code(p_tipo, p_fecha) INTO v_generated_codigo;
        IF v_generated_codigo IS NULL THEN
            message := 'Error al generar código de asiento.';
            RETURN;
        END IF;
    ELSE
        v_generated_codigo := p_codigo;
    END IF;

    -- Verificar si el asiento ya existe
    SELECT EXISTS (SELECT 1 FROM Asiento WHERE codigo = v_generated_codigo) INTO v_asiento_exists;
    IF v_asiento_exists THEN
        message := 'Ya existe un asiento con código ' || v_generated_codigo;
        RETURN;
    END IF;

    -- Calcular totales y validar existencia de cuentas
    FOR det IN SELECT * FROM jsonb_array_elements(p_detalles)
    LOOP
        v_total_debe_bs := v_total_debe_bs + COALESCE((det->>'debebs')::NUMERIC, 0);
        v_total_haber_bs := v_total_haber_bs + COALESCE((det->>'haberbs')::NUMERIC, 0);
        v_total_debe_sus := v_total_debe_sus + COALESCE((det->>'debesus')::NUMERIC, 0);
        v_total_haber_sus := v_total_haber_sus + COALESCE((det->>'habersus')::NUMERIC, 0);

        -- Validar existencia y estado de la cuenta
        SELECT EXISTS (SELECT 1 FROM Plancuenta WHERE cuenta = (det->>'cuenta') AND activo = TRUE) INTO v_cuenta_existe;
        IF NOT v_cuenta_existe THEN
            message := 'La cuenta ' || (det->>'cuenta') || ' no existe o está inactiva.';
            RETURN;
        END IF;
    END LOOP;

    -- Validar partida doble y movimientos
    IF ROUND(v_total_debe_bs, 2) <> ROUND(v_total_haber_bs, 2) THEN
        message := 'No se cumple partida doble en Bs.';
        RETURN;
    END IF;

    IF ROUND(v_total_debe_sus, 2) <> ROUND(v_total_haber_sus, 2) THEN
        message := 'No se cumple partida doble en $us.';
        RETURN;
    END IF;

    IF v_total_debe_bs = 0 AND v_total_haber_bs = 0 THEN
        message := 'El asiento debe tener al menos un movimiento.';
        RETURN;
    END IF;

    -- Insertar Asiento principal
    INSERT INTO Asiento (codigo, cta, tipo, secuencia, srs,
                         debebs, haberbs, debesus, habersus,
                         glosa, fecha, estado, usuario, fechasys)
    VALUES (v_generated_codigo, p_cta, p_tipo, p_secuencia, p_srs,
            v_total_debe_bs, v_total_haber_bs, v_total_debe_sus, v_total_haber_sus,
            p_glosa, p_fecha, COALESCE(p_estado, 'BORRADOR'), p_usuario, NOW());

    -- Insertar detalles
    i := 1;
    FOR det IN SELECT * FROM jsonb_array_elements(p_detalles)
    LOOP
        INSERT INTO Asiento_det (cod_asiento, cuenta, item,
                                 debebs, haberbs, debesus, habersus,
                                 cencosto, referencia, orden)
        VALUES (
            v_generated_codigo,
            det->>'cuenta',
            det->>'item',
            COALESCE((det->>'debebs')::NUMERIC, 0),
            COALESCE((det->>'haberbs')::NUMERIC, 0),
            COALESCE((det->>'debesus')::NUMERIC, 0),
            COALESCE((det->>'habersus')::NUMERIC, 0),
            NULLIF(det->>'cencosto', ''),
            NULLIF(det->>'referencia', ''),
            COALESCE((det->>'orden')::INT, i)
        );
        i := i + 1;
    END LOOP;

    success := TRUE;
    message := 'Asiento creado correctamente';

END;
$$;

SELECT * FROM plancuenta;
INSERT INTO Plancuenta (
    cuenta, tipo_cuenta, nivel, descrip, tipomov, moneda, fecha, debebs, haberbs, debesus, habersus, activo, usuario, fechasys
) VALUES (
    '1000', 'ACTIVO', '1', 'Caja Principal', 'DEUDOR', 'BOB', CURRENT_DATE, 0.00, 0.00, 0.00, 0.00, TRUE, 'admin', CURRENT_TIMESTAMP
);

CALL sp_create_asiento(
    NULL, 
    '1000',
    'DIARIO',
    1,
    'SRS001',
    'Asiento de prueba',
    '2024-01-01',
    'CONFIRMADO',
    'admin',
    '[{"cuenta": "110101", "debebs": 100.00, "haberbs": 0.00, "debesus": 0.00, "habersus": 0.00, "item": "Caja", "cencosto": null, "referencia": null, "orden": 1}, {"cuenta": "110301", "debebs": 0.00, "haberbs": 100.00, "debesus": 0.00, "habersus": 0.00, "item": "Ventas", "cencosto": null, "referencia": null, "orden": 2}]'::jsonb,
    NULL, NULL
);



-- sp 2

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
    END IF;

    -- Verificar que existe el cliente
    SELECT EXISTS(SELECT 1 FROM cliente WHERE id = p_cliente AND activo = TRUE) INTO v_cliente_existe;
    IF NOT v_cliente_existe THEN
        RETURN QUERY SELECT FALSE, 'El cliente especificado no existe o está inactivo', NULL::INTEGER, NULL::JSON;
    END IF;

    -- Verificar duplicados
    IF existe_venta_duplicada(p_nit, p_factura, p_fecha, p_cliente) THEN
        RETURN QUERY SELECT FALSE, 'Ya existe una venta con esos datos', NULL::INTEGER, NULL::JSON;
    END IF;

    -- Calcular valores
    SELECT neto, iva, total_calculado INTO v_neto, v_iva, v_total
    FROM calcular_valores_factura(p_importe, p_exento, p_ice);

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
    RETURN QUERY SELECT FALSE, 'Error interno al registrar venta: ' || SQLERRM, NULL::INTEGER, NULL::JSON;
END;
$$ LANGUAGE plpgsql;



SELECT * FROM sp_registrar_venta(
    '2024-06-08',
    '1234567',
    1,
    'Cliente Prueba',
    'F-001',
    'A-001',
    100.00,
    0,
    0,
    'admin'
);




-- SF 1
CREATE OR REPLACE FUNCTION balance_general(
    fecha_corte DATE,
    moneda TEXT
)
RETURNS TABLE (
    cuenta VARCHAR(100),
    descrip VARCHAR(255),
    tipo_cuenta VARCHAR(50),
    nivel VARCHAR(50),
    saldo NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.cuenta,
        p.descrip,
        p.tipo_cuenta,
        p.nivel,
        CASE
            WHEN balance_general.moneda = 'BOB' THEN
                COALESCE(SUM(ad.debebs), 0) - COALESCE(SUM(ad.haberbs), 0)
            ELSE
                COALESCE(SUM(ad.debesus), 0) - COALESCE(SUM(ad.habersus), 0)
        END AS saldo
    FROM Plancuenta p
    LEFT JOIN Asiento_det ad ON p.cuenta = ad.cuenta
    LEFT JOIN Asiento a ON ad.cod_asiento = a.codigo
    WHERE p.tipo_cuenta IN ('ACTIVO', 'PASIVO', 'PATRIMONIO')
      AND p.activo = TRUE
      AND (a.fecha IS NULL OR (a.fecha <= fecha_corte AND a.estado = 'CONFIRMADO'))
    GROUP BY p.cuenta, p.descrip, p.tipo_cuenta, p.nivel
    ORDER BY p.cuenta;
END;
$$ LANGUAGE plpgsql;


SELECT * FROM balance_general('2024-12-31', 'BOB');


-- SF 2
CREATE OR REPLACE FUNCTION calcular_saldo_cuenta(p_cuenta VARCHAR)
RETURNS NUMERIC AS $$
DECLARE
    v_debe NUMERIC := 0;
    v_haber NUMERIC := 0;
    v_saldo NUMERIC := 0;
BEGIN
    -- suma movimientos debe
    SELECT COALESCE(SUM(ad.debebs), 0) INTO v_debe
    FROM Asiento_det ad
    JOIN Asiento a ON ad.cod_asiento = a.codigo
    WHERE ad.cuenta = p_cuenta AND a.estado = 'CONFIRMADO';

    -- suma movimientos haber
    SELECT COALESCE(SUM(ad.haberbs), 0) INTO v_haber
    FROM Asiento_det ad
    JOIN Asiento a ON ad.cod_asiento = a.codigo
    WHERE ad.cuenta = p_cuenta AND a.estado = 'CONFIRMADO';

    -- calculo saldo segun tipo de cuenta
    SELECT
        CASE
            WHEN pc.tipomov = 'DEUDOR' THEN (v_debe - v_haber)
            WHEN pc.tipomov = 'ACREEDOR' THEN (v_haber - v_debe)
            ELSE (v_debe - v_haber)
        END INTO v_saldo
    FROM Plancuenta pc
    WHERE pc.cuenta = p_cuenta;

    RETURN COALESCE(v_saldo, 0);
END;
$$ LANGUAGE plpgsql;


SELECT calcular_saldo_cuenta('110101');



-- V 1
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


select * from v_resumen_ventas_periodo;



-- V 2
CREATE OR REPLACE VIEW Vista_AsientosConDetalles AS
SELECT
    a.codigo,
    a.fecha,
    a.glosa,
    a.estado,
    ad.cuenta,
    pc.descrip as cuenta_descripcion,
    ad.debebs,
    ad.haberbs,
    ad.referencia
FROM Asiento a, Asiento_det ad, Plancuenta pc
WHERE a.codigo = ad.cod_asiento
  AND ad.cuenta = pc.cuenta
ORDER BY a.fecha, a.codigo, ad.orden;


SELECT * FROM Vista_AsientosConDetalles;



-- -- C1
CREATE OR REPLACE FUNCTION sp_cursor_obtener_terceros(p_tipo VARCHAR DEFAULT NULL)
RETURNS TABLE (
    tipo_tercero VARCHAR, 
    id_tercero INT,
    razon_social VARCHAR,
    nit_tercero VARCHAR,
    telf_tercero VARCHAR,
    celular_tercero VARCHAR,
    email_tercero VARCHAR,
    pais_tercero VARCHAR,
    depto_tercero VARCHAR,
    domicilio_tercero TEXT,
    usuario_creador VARCHAR,
    fecha_sistema TIMESTAMP
)
LANGUAGE plpgsql
AS $$
DECLARE
    cur_clientes CURSOR FOR
        SELECT
            'cliente' AS tipo,
            c.id,
            c.razon,
            c.nit,
            c.telf,
            c.celular,
            c.email,
            c.pais,
            c.depto,
            c.domicilio,
            c.usuario,
            c.fechasys
        FROM cliente c
        ORDER BY c.razon;

    cur_proveedores CURSOR FOR
        SELECT
            'proveedor' AS tipo,
            p.id,
            p.razon,
            p.nit,
            p.telf,
            p.celular,
            p.email,
            p.pais,
            p.depto,
            p.domicilio,
            p.usuario,
            p.fechasys
        FROM proveedor p
        ORDER BY p.razon;

    v_tipo VARCHAR;
    v_id INT;
    v_razon VARCHAR;
    v_nit VARCHAR;
    v_telf VARCHAR;
    v_celular VARCHAR;
    v_email VARCHAR;
    v_pais VARCHAR;
    v_depto VARCHAR;
    v_domicilio TEXT;
    v_usuario VARCHAR;
    v_fechasys TIMESTAMP;

BEGIN
    IF p_tipo IS NULL OR p_tipo = 'cliente' THEN
        OPEN cur_clientes;
        LOOP
            FETCH cur_clientes INTO v_tipo, v_id, v_razon, v_nit, v_telf, v_celular, v_email, v_pais, v_depto, v_domicilio, v_usuario, v_fechasys;
            EXIT WHEN NOT FOUND;

            tipo_tercero := v_tipo;
            id_tercero := v_id;
            razon_social := v_razon;
            nit_tercero := v_nit;
            telf_tercero := v_telf;
            celular_tercero := v_celular;
            email_tercero := v_email;
            pais_tercero := v_pais;
            depto_tercero := v_depto;
            domicilio_tercero := v_domicilio;
            usuario_creador := v_usuario;
            fecha_sistema := v_fechasys;

            RETURN NEXT;
        END LOOP;
        CLOSE cur_clientes;
    END IF;

    IF p_tipo IS NULL OR p_tipo = 'proveedor' THEN
        OPEN cur_proveedores;
        LOOP
            FETCH cur_proveedores INTO v_tipo, v_id, v_razon, v_nit, v_telf, v_celular, v_email, v_pais, v_depto, v_domicilio, v_usuario, v_fechasys;
            EXIT WHEN NOT FOUND;

            tipo_tercero := v_tipo;
            id_tercero := v_id;
            razon_social := v_razon;
            nit_tercero := v_nit;
            telf_tercero := v_telf;
            celular_tercero := v_celular;
            email_tercero := v_email;
            pais_tercero := v_pais;
            depto_tercero := v_depto;
            domicilio_tercero := v_domicilio;
            usuario_creador := v_usuario;
            fecha_sistema := v_fechasys;

            RETURN NEXT;
        END LOOP;
        CLOSE cur_proveedores;
    END IF;
END;
$$;


SELECT * FROM sp_cursor_obtener_terceros();
SELECT * FROM sp_cursor_obtener_terceros('cliente'); 
SELECT * FROM sp_cursor_obtener_terceros('proveedor'); 


-- C 2

CREATE OR REPLACE FUNCTION sp_cursor_obtener_asientos(
    p_fecha_desde DATE DEFAULT NULL,
    p_fecha_hasta DATE DEFAULT NULL,
    p_tipo VARCHAR(20) DEFAULT NULL,
    p_estado VARCHAR(20) DEFAULT NULL,
    p_codigo_ilike VARCHAR(255) DEFAULT NULL
)
RETURNS TABLE (
    codigo VARCHAR(50), cta VARCHAR(50), tipo VARCHAR(20), secuencia INT, srs VARCHAR(100),
    debebs NUMERIC(18, 4), haberbs NUMERIC(18, 4), debesus NUMERIC(18, 4), habersus NUMERIC(18, 4),
    glosa TEXT, fecha DATE, estado VARCHAR(20), usuario VARCHAR(50), fechasys TIMESTAMP,
    usuario_confirmacion VARCHAR(50), fecha_confirmacion TIMESTAMP, tipo_descrip VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
DECLARE
    asientos_cursor CURSOR FOR
        SELECT
            a.codigo, a.cta, a.tipo, a.secuencia, a.srs,
            a.debebs, a.haberbs, a.debesus, a.habersus,
            a.glosa, a.fecha, a.estado, a.usuario, a.fechasys,
            a.usuario_confirmacion, a.fecha_confirmacion,
            ta.descrip AS tipo_descrip
        FROM Asiento a
        LEFT JOIN TipoAsiento ta ON a.tipo = ta.codigo
        WHERE
            (p_fecha_desde IS NULL OR a.fecha >= p_fecha_desde) AND
            (p_fecha_hasta IS NULL OR a.fecha <= p_fecha_hasta) AND
            (p_tipo IS NULL OR a.tipo = p_tipo) AND
            (p_estado IS NULL OR a.estado = p_estado) AND
            (p_codigo_ilike IS NULL OR a.codigo ILIKE p_codigo_ilike)
        ORDER BY a.fecha DESC, a.codigo DESC;
    
    asiento_record RECORD;
BEGIN
    OPEN asientos_cursor;
    LOOP
        FETCH asientos_cursor INTO asiento_record;
        EXIT WHEN NOT FOUND;
        
        codigo := asiento_record.codigo;
        cta := asiento_record.cta;
        tipo := asiento_record.tipo;
        secuencia := asiento_record.secuencia;
        srs := asiento_record.srs;
        debebs := asiento_record.debebs;
        haberbs := asiento_record.haberbs;
        debesus := asiento_record.debesus;
        habersus := asiento_record.habersus;
        glosa := asiento_record.glosa;
        fecha := asiento_record.fecha;
        estado := asiento_record.estado;
        usuario := asiento_record.usuario;
        fechasys := asiento_record.fechasys;
        usuario_confirmacion := asiento_record.usuario_confirmacion;
        fecha_confirmacion := asiento_record.fecha_confirmacion;
        tipo_descrip := asiento_record.tipo_descrip;
        
        RETURN NEXT;
    END LOOP;
    CLOSE asientos_cursor;
END;
$$;



SELECT * FROM sp_cursor_obtener_asientos('2024-01-01', '2024-12-31', NULL, 'CONFIRMADO', NULL);