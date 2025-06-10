-- 1. CURSOR

-- mediante un cursor obtener los asientos contables con filtros
-- Esta función permite filtrar por fecha, tipo, estado y código
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

-- 2. FUNCIÓN sp_obtener_todas_cuentas() CONVERTIDA A CURSOR
-- Útil para grandes planes de cuenta
CREATE OR REPLACE FUNCTION sp_cursor_obtener_todas_cuentas(p_empresa_id INT)
RETURNS TABLE (
    cuenta VARCHAR,
    tipo_cuenta VARCHAR,
    nivel INT,
    descrip VARCHAR,
    tipomov VARCHAR,
    moneda VARCHAR,
    fecha DATE,
    usuario VARCHAR,
    fechasys TIMESTAMP,
    tipo_cuenta_descrip VARCHAR,
    moneda_descrip VARCHAR,
    tipomov_descrip VARCHAR
) 
LANGUAGE plpgsql
AS $$
DECLARE
    cuentas_cursor CURSOR FOR
        SELECT p.cuenta, p.tipo_cuenta, p.nivel, p.descrip, p.tipomov, p.moneda, 
               p.fecha, p.usuario, p.fechasys,
               tc.descrip AS tipo_cuenta_descrip,
               m.descrip AS moneda_descrip,
               mv.descrip AS tipomov_descrip
        FROM Plancuenta p
        LEFT JOIN TipoCuenta tc ON p.tipo_cuenta = tc.codigo
        LEFT JOIN Moneda m ON p.moneda = m.codigo
        LEFT JOIN MovCuenta mv ON p.tipomov = mv.codigo
        WHERE p.empresa_id = p_empresa_id
        ORDER BY p.cuenta;
    
    cuenta_record RECORD;
BEGIN
    OPEN cuentas_cursor;
    LOOP
        FETCH cuentas_cursor INTO cuenta_record;
        EXIT WHEN NOT FOUND;
        
        -- Asignar valores
        cuenta := cuenta_record.cuenta;
        tipo_cuenta := cuenta_record.tipo_cuenta;
        nivel := cuenta_record.nivel;
        descrip := cuenta_record.descrip;
        tipomov := cuenta_record.tipomov;
        moneda := cuenta_record.moneda;
        fecha := cuenta_record.fecha;
        usuario := cuenta_record.usuario;
        fechasys := cuenta_record.fechasys;
        tipo_cuenta_descrip := cuenta_record.tipo_cuenta_descrip;
        moneda_descrip := cuenta_record.moneda_descrip;
        tipomov_descrip := cuenta_record.tipomov_descrip;
        
        RETURN NEXT;
    END LOOP;
    CLOSE cuentas_cursor;
END;
$$;

-- 3. FUNCIÓN MEJORADA para obtener terceros con filtros adicionales
-- Esta versión permite más control y filtros dinámicos
CREATE OR REPLACE FUNCTION sp_cursor_obtener_terceros(
    p_tipo VARCHAR DEFAULT NULL,
    p_pais VARCHAR DEFAULT NULL,
    p_email_like VARCHAR DEFAULT NULL,
    p_limit INT DEFAULT NULL
)
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
            c.id, c.razon, c.nit, c.telf, c.celular, c.email,
            c.pais, c.depto, c.domicilio, c.usuario, c.fechasys
        FROM cliente c
        WHERE 
            (p_pais IS NULL OR c.pais = p_pais) AND
            (p_email_like IS NULL OR c.email ILIKE '%' || p_email_like || '%')
        ORDER BY c.razon;

    cur_proveedores CURSOR FOR
        SELECT
            'proveedor' AS tipo,
            p.id, p.razon, p.nit, p.telf, p.celular, p.email,
            p.pais, p.depto, p.domicilio, p.usuario, p.fechasys
        FROM proveedor p
        WHERE 
            (p_pais IS NULL OR p.pais = p_pais) AND
            (p_email_like IS NULL OR p.email ILIKE '%' || p_email_like || '%')
        ORDER BY p.razon;

    tercero_record RECORD;
    contador INT := 0;
BEGIN
    -- Procesar clientes
    IF p_tipo IS NULL OR p_tipo = 'cliente' THEN
        OPEN cur_clientes;
        LOOP
            FETCH cur_clientes INTO tercero_record;
            EXIT WHEN NOT FOUND;
            
            -- Aplicar límite si se especifica
            IF p_limit IS NOT NULL THEN
                contador := contador + 1;
                IF contador > p_limit THEN
                    EXIT;
                END IF;
            END IF;
            
            -- Asignar valores
            tipo_tercero := tercero_record.tipo;
            id_tercero := tercero_record.id;
            razon_social := tercero_record.razon;
            nit_tercero := tercero_record.nit;
            telf_tercero := tercero_record.telf;
            celular_tercero := tercero_record.celular;
            email_tercero := tercero_record.email;
            pais_tercero := tercero_record.pais;
            depto_tercero := tercero_record.depto;
            domicilio_tercero := tercero_record.domicilio;
            usuario_creador := tercero_record.usuario;
            fecha_sistema := tercero_record.fechasys;
            
            RETURN NEXT;
        END LOOP;
        CLOSE cur_clientes;
    END IF;

    -- Procesar proveedores
    IF p_tipo IS NULL OR p_tipo = 'proveedor' THEN
        OPEN cur_proveedores;
        LOOP
            FETCH cur_proveedores INTO tercero_record;
            EXIT WHEN NOT FOUND;
            
            -- Aplicar límite si se especifica (continuar contando desde clientes)
            IF p_limit IS NOT NULL THEN
                contador := contador + 1;
                IF contador > p_limit THEN
                    EXIT;
                END IF;
            END IF;
            
            -- Asignar valores
            tipo_tercero := tercero_record.tipo;
            id_tercero := tercero_record.id;
            razon_social := tercero_record.razon;
            nit_tercero := tercero_record.nit;
            telf_tercero := tercero_record.telf;
            celular_tercero := tercero_record.celular;
            email_tercero := tercero_record.email;
            pais_tercero := tercero_record.pais;
            depto_tercero := tercero_record.depto;
            domicilio_tercero := tercero_record.domicilio;
            usuario_creador := tercero_record.usuario;
            fecha_sistema := tercero_record.fechasys;
            
            RETURN NEXT;
        END LOOP;
        CLOSE cur_proveedores;
    END IF;
END;
$$;

-- 4. FUNCIÓN PARA OBTENER CONTACTOS DE TODOS LOS TERCEROS CON CURSOR
-- Útil cuando se necesita un reporte consolidado de contactos
CREATE OR REPLACE FUNCTION sp_cursor_obtener_todos_contactos()
RETURNS TABLE (
    tipo_tercero VARCHAR,
    id_tercero INT,
    razon_tercero VARCHAR,
    nombre_contacto VARCHAR,
    telf_contacto VARCHAR,
    celular_contacto VARCHAR,
    email_contacto VARCHAR,
    fecha_creacion TIMESTAMP
)
LANGUAGE plpgsql
AS $$
DECLARE
    cur_contactos_clientes CURSOR FOR
        SELECT 
            'cliente' AS tipo,
            c.id AS id_tercero,
            c.razon AS razon_tercero,
            cc.nombre AS nombre_contacto,
            cc.telf AS telf_contacto,
            cc.celular AS celular_contacto,
            cc.email AS email_contacto,
            cc.fechasys AS fecha_creacion
        FROM cliente c
        INNER JOIN Cliente_contacto cc ON c.id = cc.id_cliente
        ORDER BY c.razon, cc.nombre;
    
    cur_contactos_proveedores CURSOR FOR
        SELECT 
            'proveedor' AS tipo,
            p.id AS id_tercero,
            p.razon AS razon_tercero,
            pc.nombre AS nombre_contacto,
            pc.telf AS telf_contacto,
            pc.celular AS celular_contacto,
            pc.email AS email_contacto,
            pc.fechasys AS fecha_creacion
        FROM proveedor p
        INNER JOIN Proveedor_contacto pc ON p.id = pc.id_proveedor
        ORDER BY p.razon, pc.nombre;
    
    contacto_record RECORD;
BEGIN
    -- Procesar contactos de clientes
    OPEN cur_contactos_clientes;
    LOOP
        FETCH cur_contactos_clientes INTO contacto_record;
        EXIT WHEN NOT FOUND;
        
        tipo_tercero := contacto_record.tipo;
        id_tercero := contacto_record.id_tercero;
        razon_tercero := contacto_record.razon_tercero;
        nombre_contacto := contacto_record.nombre_contacto;
        telf_contacto := contacto_record.telf_contacto;
        celular_contacto := contacto_record.celular_contacto;
        email_contacto := contacto_record.email_contacto;
        fecha_creacion := contacto_record.fecha_creacion;
        
        RETURN NEXT;
    END LOOP;
    CLOSE cur_contactos_clientes;
    
    -- Procesar contactos de proveedores
    OPEN cur_contactos_proveedores;
    LOOP
        FETCH cur_contactos_proveedores INTO contacto_record;
        EXIT WHEN NOT FOUND;
        
        tipo_tercero := contacto_record.tipo;
        id_tercero := contacto_record.id_tercero;
        razon_tercero := contacto_record.razon_tercero;
        nombre_contacto := contacto_record.nombre_contacto;
        telf_contacto := contacto_record.telf_contacto;
        celular_contacto := contacto_record.celular_contacto;
        email_contacto := contacto_record.email_contacto;
        fecha_creacion := contacto_record.fecha_creacion;
        
        RETURN NEXT;
    END LOOP;
    CLOSE cur_contactos_proveedores;
END;
$$;

-- ====================================================================
-- EJEMPLOS DE USO DE LAS FUNCIONES CON CURSOR
-- ====================================================================

-- Obtener asientos con cursor
SELECT * FROM sp_cursor_obtener_asientos('2024-01-01', '2024-12-31', NULL, 'CONFIRMADO', NULL);

-- Obtener cuentas con cursor
SELECT * FROM sp_cursor_obtener_todas_cuentas(1);

-- Obtener terceros con filtros adicionales
SELECT * FROM sp_cursor_obtener_terceros('cliente', 'Bolivia', 'gmail', 100);

-- Obtener todos los contactos
SELECT * FROM sp_cursor_obtener_todos_contactos();





---- PROCEDIMIENTOS
-- mediante un procedimiento almacenado crear un asiento contable
-- Este procedimiento permite crear un asiento contable con detalles    
CREATE OR REPLACE PROCEDURE sp_create_asiento(
    IN p_codigo VARCHAR(50),
    IN p_cta VARCHAR(50),
    IN p_tipo VARCHAR(20),
    IN p_secuencia INT,
    IN p_srs VARCHAR(100),
    IN p_glosa TEXT,
    IN p_fecha DATE,
    IN p_estado VARCHAR(20),
    IN p_usuario VARCHAR(50),
    IN p_detalles JSONB, -- Array of detail objects
    OUT success BOOLEAN,
    OUT message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_debe_bs NUMERIC(18, 4) := 0;
    v_total_haber_bs NUMERIC(18, 4) := 0;
    v_total_debe_sus NUMERIC(18, 4) := 0;
    v_total_haber_sus NUMERIC(18, 4) := 0;
    det JSONB;
    v_cuenta_existe BOOLEAN;
    v_asiento_exists BOOLEAN;
    v_generated_codigo VARCHAR(50);
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

    -- Calcular totales y validar partida doble
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
    FOR det IN SELECT * FROM jsonb_array_elements(p_detalles) WITH ORDINALITY AS i
    LOOP
        INSERT INTO Asiento_det (cod_asiento, cuenta, item,
                                 debebs, haberbs, debesus, habersus,
                                 cencosto, referencia, orden)
        VALUES (v_generated_codigo, det->>'cuenta', det->>'item',
                COALESCE((det->>'debebs')::NUMERIC, 0), COALESCE((det->>'haberbs')::NUMERIC, 0),
                COALESCE((det->>'debesus')::NUMERIC, 0), COALESCE((det->>'habersus')::NUMERIC, 0),
                det->>'cencosto', det->>'referencia', COALESCE((det->>'orden')::INT, i));
    END LOOP;

    success := TRUE;
    message := 'Asiento creado correctamente';

END;
$$;
-- usar el procedimiento
CALL sp_create_asiento(
    p_codigo := NULL,
    p_cta := '1000',
    p_tipo := 'DIARIO',
    p_secuencia := 1,
    p_srs := 'SRS001',
    p_glosa := 'Asiento de prueba',
    p_fecha := '2024-01-01',
    p_estado := 'CONFIRMADO',
    p_usuario := 'admin',
    p_detalles := '[{"cuenta": "1000", "debebs": 100.00, "haberbs": 0.00, "debesus": 0.00, "habersus": 0.00, "item": "Caja", "cencosto": null, "referencia": null, "orden": 1}, {"cuenta": "2000", "debebs": 0.00, "haberbs": 100.00, "debesus": 0.00, "habersus": 0.00, "item": "Ventas", "cencosto": null, "referencia": null, "orden": 2}]'
);

-- mediante un procedimiento almacenado registrar una venta 

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
    RETURN QUERY SELECT FALSE, 'Error interno al registrar venta: ' || SQLERRM, NULL::INTEGER, NULL::JSON;
END;
$$ LANGUAGE plpgsql;


-- uso del procedimiento
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