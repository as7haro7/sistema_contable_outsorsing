-- ASIENTOS CONTABLES --

-- functions/get_active_asiento_types.sql
CREATE OR REPLACE FUNCTION obtener_tipos_asiento()
RETURNS TABLE (
    codigo VARCHAR(20),
    descrip VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT ta.codigo, ta.descrip
    FROM TipoAsiento ta
    WHERE ta.activo = TRUE
    ORDER BY ta.codigo;
END;
$$;


-- functions/get_asientos.sql
CREATE OR REPLACE FUNCTION obtener_asientos(
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
BEGIN
    RETURN QUERY
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
END;
$$;


-- procedures/create_asiento_sp.sql
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

    -- Check if asiento code already exists if provided, otherwise generate
    IF p_codigo IS NULL OR p_codigo = '' THEN
        -- Call a separate function to generate code if needed, or handle here
        SELECT get_next_asiento_code(p_tipo, p_fecha) INTO v_generated_codigo;
        IF v_generated_codigo IS NULL THEN
            message := 'Error al generar código de asiento.';
            RETURN;
        END IF;
    ELSE
        v_generated_codigo := p_codigo;
    END IF;

    SELECT EXISTS (SELECT 1 FROM Asiento WHERE codigo = v_generated_codigo) INTO v_asiento_exists;
    IF v_asiento_exists THEN
        message := 'Ya existe un asiento con código ' || v_generated_codigo;
        RETURN;
    END IF;

    -- Calculate totals and validate partida doble from JSONB details
    FOR det IN SELECT * FROM jsonb_array_elements(p_detalles)
    LOOP
        v_total_debe_bs := v_total_debe_bs + COALESCE((det->>'debebs')::NUMERIC, 0);
        v_total_haber_bs := v_total_haber_bs + COALESCE((det->>'haberbs')::NUMERIC, 0);
        v_total_debe_sus := v_total_debe_sus + COALESCE((det->>'debesus')::NUMERIC, 0);
        v_total_haber_sus := v_total_haber_sus + COALESCE((det->>'habersus')::NUMERIC, 0);

        -- Validate if account exists and is active
        SELECT EXISTS (SELECT 1 FROM Plancuenta WHERE cuenta = (det->>'cuenta') AND activo = TRUE) INTO v_cuenta_existe;
        IF NOT v_cuenta_existe THEN
            message := 'La cuenta ' || (det->>'cuenta') || ' no existe o está inactiva.';
            RETURN;
        END IF;
    END LOOP;

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

    -- Insert Asiento principal
    INSERT INTO Asiento (codigo, cta, tipo, secuencia, srs,
                         debebs, haberbs, debesus, habersus,
                         glosa, fecha, estado, usuario, fechasys)
    VALUES (v_generated_codigo, p_cta, p_tipo, p_secuencia, p_srs,
            v_total_debe_bs, v_total_haber_bs, v_total_debe_sus, v_total_haber_sus,
            p_glosa, p_fecha, COALESCE(p_estado, 'CONFIRMADO'), p_usuario, NOW());

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

EXCEPTION
    WHEN OTHERS THEN
        success := FALSE;
        message := 'Error al crear asiento: ' || SQLERRM;
        -- No need for explicit ROLLBACK in PL/pgSQL procedures, as errors outside EXCEPTION blocks
        -- typically cause an implicit rollback for the current transaction block if not caught.
        -- For true transaction control with multiple DMLs, consider using explicit BEGIN/COMMIT/ROLLBACK in the caller.
        -- However, for a single procedure, the default behavior often suffices.
END;
$$;




------ PLAN DE CUENTAS ----
-- Option 1: Function returning SETOF record (requires explicit column definition in SELECT)
CREATE OR REPLACE FUNCTION sp_obtener_todas_cuentas(p_empresa_id INT)
RETURNS SETOF Plancuenta AS $$
BEGIN
    RETURN QUERY
    SELECT p.*,
           tc.descrip AS tipo_cuenta_descrip,
           m.descrip AS moneda_descrip,
           mv.descrip AS tipomov_descrip
    FROM Plancuenta p
    LEFT JOIN TipoCuenta tc ON p.tipo_cuenta = tc.codigo
    LEFT JOIN Moneda m ON p.moneda = m.codigo
    LEFT JOIN MovCuenta mv ON p.tipomov = mv.codigo
    WHERE p.empresa_id = p_empresa_id -- Assuming Plancuenta has empresa_id
    ORDER BY p.cuenta;
END;
$$ LANGUAGE plpgsql;

-- Option 2: Function returning TABLE (more explicit column names)
CREATE OR REPLACE FUNCTION sp_obtener_todas_cuentas(p_empresa_id INT)
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
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.cuenta, p.tipo_cuenta, p.nivel, p.descrip, p.tipomov, p.moneda, p.fecha, p.usuario, p.fechasys,
           tc.descrip AS tipo_cuenta_descrip,
           m.descrip AS moneda_descrip,
           mv.descrip AS tipomov_descrip
    FROM Plancuenta p
    LEFT JOIN TipoCuenta tc ON p.tipo_cuenta = tc.codigo
    LEFT JOIN Moneda m ON p.moneda = m.codigo
    LEFT JOIN MovCuenta mv ON p.tipomov = mv.codigo
    WHERE p.empresa_id = p_empresa_id
    ORDER BY p.cuenta;
END;
$$ LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION sp_obtener_cuenta_por_codigo(p_empresa_id INT, p_codigo VARCHAR)
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
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.cuenta, p.tipo_cuenta, p.nivel, p.descrip, p.tipomov, p.moneda, p.fecha, p.usuario, p.fechasys,
           tc.descrip AS tipo_cuenta_descrip,
           m.descrip AS moneda_descrip,
           mv.descrip AS tipomov_descrip
    FROM Plancuenta p
    LEFT JOIN TipoCuenta tc ON p.tipo_cuenta = tc.codigo
    LEFT JOIN Moneda m ON p.moneda = m.codigo
    LEFT JOIN MovCuenta mv ON p.tipomov = mv.codigo
    WHERE p.empresa_id = p_empresa_id AND p.cuenta = p_codigo;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE PROCEDURE sp_crear_cuenta(
    p_empresa_id INT,
    p_cuenta VARCHAR,
    p_tipo_cuenta VARCHAR,
    p_nivel INT,
    p_descrip VARCHAR,
    p_tipomov VARCHAR,
    p_moneda VARCHAR
    -- p_usuario VARCHAR -- If not handled by trigger
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO Plancuenta (empresa_id, cuenta, tipo_cuenta, nivel, descrip, tipomov, moneda)
    VALUES (p_empresa_id, p_cuenta, p_tipo_cuenta, p_nivel, p_descrip, p_tipomov, p_moneda);
    -- If trigger handles usuario and fechasys, these are omitted here.
    -- If not, you'd include: , CURRENT_DATE, p_usuario, NOW()
END;
$$;




CREATE OR REPLACE PROCEDURE sp_actualizar_cuenta(
    p_empresa_id INT,
    p_codigo VARCHAR,
    p_descrip VARCHAR,
    p_tipo_cuenta VARCHAR,
    p_nivel INT,
    p_tipomov VARCHAR,
    p_moneda VARCHAR
    -- p_usuario VARCHAR -- If not handled by trigger
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE Plancuenta
    SET descrip = p_descrip,
        tipo_cuenta = p_tipo_cuenta,
        nivel = p_nivel,
        tipomov = p_tipomov,
        moneda = p_moneda
        -- usuario = p_usuario, -- If not handled by trigger
        -- fechasys = NOW()     -- If not handled by trigger
    WHERE empresa_id = p_empresa_id AND cuenta = p_codigo;
END;
$$;



CREATE OR REPLACE PROCEDURE sp_eliminar_cuenta(p_empresa_id INT, p_codigo VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM Plancuenta
    WHERE empresa_id = p_empresa_id AND cuenta = p_codigo;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_eliminar_cuenta(p_empresa_id INT, p_codigo VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM Plancuenta
    WHERE empresa_id = p_empresa_id AND cuenta = p_codigo;
END;
$$;



CREATE OR REPLACE FUNCTION sp_tiene_movimientos(p_empresa_id INT, p_codigo VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    has_movements BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM Asiento_det
        WHERE empresa_id = p_empresa_id AND cuenta = p_codigo
        LIMIT 1
    ) INTO has_movements;
    RETURN has_movements;
END;
$$ LANGUAGE plpgsql;

-- TRIGER

CREATE OR REPLACE FUNCTION set_plancuenta_audit_fields()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.fecha := CURRENT_DATE;
        NEW.fechasys := NOW();
        -- NEW.usuario := current_user; -- Or pass from application if you want to control it from client
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.fechasys := NOW();
        -- NEW.usuario := current_user;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER plancuenta_audit_trigger
BEFORE INSERT OR UPDATE ON Plancuenta
FOR EACH ROW EXECUTE FUNCTION set_plancuenta_audit_fields();


















--------------- TERCEROS ---------------
-- Función modificada para usar un cursor explícito (ejemplo educativo)
CREATE OR REPLACE FUNCTION sp_get_all_terceros_with_cursor(p_tipo VARCHAR DEFAULT NULL)
RETURNS TABLE (
    tipo VARCHAR,
    id INT,
    razon VARCHAR,
    nit VARCHAR,
    telf VARCHAR,
    celular VARCHAR,
    email VARCHAR,
    pais VARCHAR,
    depto VARCHAR,
    domicilio TEXT,
    usuario VARCHAR,
    fechasys TIMESTAMP
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Declaración de un cursor para clientes
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

    -- Declaración de un cursor para proveedores
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

    -- Variable para almacenar cada fila del cursor
    r RECORD;
BEGIN
    IF p_tipo IS NULL OR p_tipo = 'cliente' THEN
        OPEN cur_clientes;
        LOOP
            FETCH cur_clientes INTO r;
            EXIT WHEN NOT FOUND;
            -- Añade la fila al conjunto de resultados de la función
            RETURN NEXT r;
        END LOOP;
        CLOSE cur_clientes;
    END IF;

    IF p_tipo IS NULL OR p_tipo = 'proveedor' THEN
        OPEN cur_proveedores;
        LOOP
            FETCH cur_proveedores INTO r;
            EXIT WHEN NOT FOUND;
            -- Añade la fila al conjunto de resultados de la función
            RETURN NEXT r;
        END LOOP;
        CLOSE cur_proveedores;
    END IF;
END;
$$;




-- revisar 

-- *** 2. Triggers (Ejemplo para fechasys) ***
-- Se pueden crear triggers para manejar la actualización de `fechasys` automáticamente.

-- Trigger para cliente (al insertar o actualizar)
CREATE OR REPLACE FUNCTION set_fechasys_cliente()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fechasys = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_set_fechasys_cliente
BEFORE INSERT OR UPDATE ON cliente
FOR EACH ROW
EXECUTE FUNCTION set_fechasys_cliente();

-- Trigger para proveedor (al insertar o actualizar)
CREATE OR REPLACE FUNCTION set_fechasys_proveedor()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fechasys = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_set_fechasys_proveedor
BEFORE INSERT OR UPDATE ON proveedor
FOR EACH ROW
EXECUTE FUNCTION set_fechasys_proveedor();

-- Trigger para Cliente_contacto (al insertar o actualizar)
CREATE OR REPLACE FUNCTION set_fechasys_cliente_contacto()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fechasys = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_set_fechasys_cliente_contacto
BEFORE INSERT OR UPDATE ON Cliente_contacto
FOR EACH ROW
EXECUTE FUNCTION set_fechasys_cliente_contacto();

-- Trigger para Proveedor_contacto (al insertar o actualizar)
CREATE OR REPLACE FUNCTION set_fechasys_proveedor_contacto()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fechasys = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_set_fechasys_proveedor_contacto
BEFORE INSERT OR UPDATE ON Proveedor_contacto
FOR EACH ROW
EXECUTE FUNCTION set_fechasys_proveedor_contacto();


-- *** 3. Funciones y Procedimientos Almacenados (SPs y SFs) ***

-- SP para listar todos los terceros (clientes y/o proveedores)
-- Demuestra el uso de un cursor implícito o explícito si se necesitara más control
-- Función modificada para usar un cursor explícito y corregir el error RETURN NEXT
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

-- SF para obtener cliente por ID
CREATE OR REPLACE FUNCTION sf_get_cliente_by_id(p_id INT)
RETURNS SETOF cliente
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY SELECT * FROM cliente WHERE id = p_id;
END;
$$;

-- SF para obtener proveedor por ID
CREATE OR REPLACE FUNCTION sf_get_proveedor_by_id(p_id INT)
RETURNS SETOF proveedor
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY SELECT * FROM proveedor WHERE id = p_id;
END;
$$;

-- SP para crear un nuevo cliente
CREATE OR REPLACE FUNCTION sp_create_cliente(
    p_razon VARCHAR, p_nit VARCHAR, p_telf VARCHAR, p_celular VARCHAR,
    p_email VARCHAR, p_pais VARCHAR, p_depto VARCHAR, p_domicilio TEXT, p_usuario VARCHAR
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO cliente (razon, nit, telf, celular, email, pais, depto, domicilio, usuario)
    VALUES (p_razon, p_nit, p_telf, p_celular, p_email, p_pais, p_depto, p_domicilio, p_usuario)
    RETURNING id INTO new_id;
    RETURN new_id;
END;
$$;

-- SP para crear un nuevo proveedor
CREATE OR REPLACE FUNCTION sp_create_proveedor(
    p_razon VARCHAR, p_nit VARCHAR, p_autorizacion VARCHAR, p_telf VARCHAR, p_celular VARCHAR,
    p_email VARCHAR, p_pais VARCHAR, p_depto VARCHAR, p_domicilio TEXT, p_usuario VARCHAR
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO proveedor (razon, nit, autorizacion, telf, celular, email, pais, depto, domicilio, usuario)
    VALUES (p_razon, p_nit, p_autorizacion, p_telf, p_celular, p_email, p_pais, p_depto, p_domicilio, p_usuario)
    RETURNING id INTO new_id;
    RETURN new_id;
END;
$$;

-- SP para actualizar un cliente
CREATE OR REPLACE FUNCTION sp_update_cliente(
    p_id INT, p_razon VARCHAR, p_nit VARCHAR, p_telf VARCHAR, p_celular VARCHAR,
    p_email VARCHAR, p_pais VARCHAR, p_depto VARCHAR, p_domicilio TEXT, p_usuario VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE cliente
    SET
        razon = p_razon,
        nit = p_nit,
        telf = p_telf,
        celular = p_celular,
        email = p_email,
        pais = p_pais,
        depto = p_depto,
        domicilio = p_domicilio,
        usuario = p_usuario -- El trigger actualizará fechasys
    WHERE id = p_id;
    RETURN FOUND; -- Retorna true si se actualizó una fila
END;
$$;

-- SP para actualizar un proveedor
CREATE OR REPLACE FUNCTION sp_update_proveedor(
    p_id INT, p_razon VARCHAR, p_nit VARCHAR, p_autorizacion VARCHAR, p_telf VARCHAR, p_celular VARCHAR,
    p_email VARCHAR, p_pais VARCHAR, p_depto VARCHAR, p_domicilio TEXT, p_usuario VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE proveedor
    SET
        razon = p_razon,
        nit = p_nit,
        autorizacion = p_autorizacion,
        telf = p_telf,
        celular = p_celular,
        email = p_email,
        pais = p_pais,
        depto = p_depto,
        domicilio = p_domicilio,
        usuario = p_usuario -- El trigger actualizará fechasys
    WHERE id = p_id;
    RETURN FOUND;
END;
$$;

-- SP para "eliminar" (simplemente DELETE en este ejemplo) un cliente
CREATE OR REPLACE FUNCTION sp_delete_cliente(p_id INT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    -- Se podría implementar una eliminación lógica (e.g., actualizar un campo 'activo' a false)
    -- En este ejemplo, es una eliminación física.
    DELETE FROM cliente WHERE id = p_id;
    RETURN FOUND;
END;
$$;

-- SP para "eliminar" (simplemente DELETE en este ejemplo) un proveedor
CREATE OR REPLACE FUNCTION sp_delete_proveedor(p_id INT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    -- Se podría implementar una eliminación lógica (e.g., actualizar un campo 'activo' a false)
    -- En este ejemplo, es una eliminación física.
    DELETE FROM proveedor WHERE id = p_id;
    RETURN FOUND;
END;
$$;

-- SF para obtener contactos de cliente
CREATE OR REPLACE FUNCTION sf_get_cliente_contactos(p_id_cliente INT)
RETURNS SETOF Cliente_contacto
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY SELECT * FROM Cliente_contacto WHERE id_cliente = p_id_cliente;
END;
$$;

-- SF para obtener contactos de proveedor
CREATE OR REPLACE FUNCTION sf_get_proveedor_contactos(p_id_proveedor INT)
RETURNS SETOF Proveedor_contacto
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY SELECT * FROM Proveedor_contacto WHERE id_proveedor = p_id_proveedor;
END;
$$;

-- SP para agregar contacto a cliente
CREATE OR REPLACE FUNCTION sp_add_cliente_contacto(
    p_id_cliente INT, p_nombre VARCHAR, p_telf VARCHAR, p_celular VARCHAR, p_email VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Cliente_contacto (id_cliente, nombre, telf, celular, email)
    VALUES (p_id_cliente, p_nombre, p_telf, p_celular, p_email);
    RETURN TRUE;
END;
$$;

-- SP para agregar contacto a proveedor
CREATE OR REPLACE FUNCTION sp_add_proveedor_contacto(
    p_id_proveedor INT, p_nombre VARCHAR, p_telf VARCHAR, p_celular VARCHAR, p_email VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Proveedor_contacto (id_proveedor, nombre, telf, celular, email)
    VALUES (p_id_proveedor, p_nombre, p_telf, p_celular, p_email);
    RETURN TRUE;
END;
$$;