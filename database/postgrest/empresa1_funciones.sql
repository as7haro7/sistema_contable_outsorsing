-- === 13. VISTAS ÚTILES PARA PRÁCTICA ===

-- 1. Vista para el balance de comprobación
CREATE OR REPLACE VIEW Vista_BalanceComprobacion AS
SELECT
    p.cuenta,
    p.descrip,
    p.tipo_cuenta,
    p.debebs,
    p.haberbs,
    (p.debebs - p.haberbs) as saldo
FROM Plancuenta p
WHERE p.activo = TRUE
ORDER BY p.cuenta;

-- 2. Vista para el resumen de ventas por cliente
CREATE OR REPLACE VIEW Vista_ResumenVentasPorCliente AS
SELECT
    c.razon,
    COUNT(lv.id) as num_facturas,
    SUM(lv.neto) as total_neto,
    SUM(lv.iva) as total_iva,
    SUM(lv.importe) as total_importe
FROM LibroVentas lv
JOIN cliente c ON lv.cliente = c.id
GROUP BY c.id, c.razon
ORDER BY total_importe DESC;

-- 3. Vista para el resumen de compras por proveedor
CREATE OR REPLACE VIEW Vista_ResumenComprasPorProveedor AS
SELECT
    p.razon,
    COUNT(lc.id) as num_facturas,
    SUM(lc.neto) as total_neto,
    SUM(lc.iva) as total_iva,
    SUM(lc.importe) as total_importe
FROM LibroCompras lc
JOIN proveedor p ON lc.proveedor = p.id
GROUP BY p.id, p.razon
ORDER BY total_importe DESC;

-- 4. Vista para los asientos contables con sus detalles
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
FROM Asiento a
JOIN Asiento_det ad ON a.codigo = ad.cod_asiento
JOIN Plancuenta pc ON ad.cuenta = pc.cuenta
ORDER BY a.fecha, a.codigo, ad.orden;

-- 5. Vista para el estado de resultados básico (Noviembre 2024)
CREATE OR REPLACE VIEW Vista_EstadoResultadosNov2024 AS
SELECT
    'INGRESOS' as concepto,
    SUM(lv.neto) as monto
FROM LibroVentas lv
WHERE lv.fecha BETWEEN '2024-11-01' AND '2024-11-30'
UNION ALL
SELECT
    'COSTOS DE VENTA' as concepto,
    SUM(ad.debebs) as monto
FROM Asiento_det ad
WHERE ad.cuenta LIKE '51%'
UNION ALL
SELECT
    'GASTOS OPERACIONALES' as concepto,
    SUM(ad.debebs) as monto
FROM Asiento_det ad
WHERE ad.cuenta LIKE '52%';


-- === 14. PROCEDIMIENTOS ALMACENADOS ÚTILES ===

-- Función para calcular el saldo de una cuenta
CREATE OR REPLACE FUNCTION calcular_saldo_cuenta(p_cuenta VARCHAR)
RETURNS NUMERIC AS $$
DECLARE
    v_debe NUMERIC := 0;
    v_haber NUMERIC := 0;
    v_saldo NUMERIC := 0;
BEGIN
    -- Sumar movimientos debe
    SELECT COALESCE(SUM(debebs), 0) INTO v_debe
    FROM Asiento_det ad
    JOIN Asiento a ON ad.cod_asiento = a.codigo
    WHERE ad.cuenta = p_cuenta AND a.estado = 'CONFIRMADO';

    -- Sumar movimientos haber
    SELECT COALESCE(SUM(haberbs), 0) INTO v_haber
    FROM Asiento_det ad
    JOIN Asiento a ON ad.cod_asiento = a.codigo
    WHERE ad.cuenta = p_cuenta AND a.estado = 'CONFIRMADO';

    -- Calcular saldo según tipo de cuenta
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

-- Función para generar código de asiento
CREATE OR REPLACE FUNCTION generar_codigo_asiento()
RETURNS VARCHAR AS $$
DECLARE
    v_numero INTEGER;
    v_codigo VARCHAR;
BEGIN
    -- Obtener el siguiente número
    SELECT COALESCE(MAX(CAST(SUBSTRING(codigo FROM 5) AS INTEGER)), 0) + 1
    INTO v_numero
    FROM Asiento
    WHERE codigo LIKE 'ASI-%';

    -- Formatear código
    v_codigo := 'ASI-' || LPAD(v_numero::TEXT, 3, '0');

    RETURN v_codigo;
END;
$$ LANGUAGE plpgsql;

-- === FIN DE DATOS DE PRUEBA ===
-- Estos datos te permitirán practicar:
-- 1. Consultas de reportes contables
-- 2. Análisis de ventas y compras
-- 3. Estados financieros básicos
-- 4. Conciliaciones bancarias
-- 5. Control de inventarios
-- 6. Gestión de cuentas por cobrar y pagar
-- 7. Cálculo de impuestos (IVA, IT)
-- 8. Presupuestos y análisis de variaciones