-- === DATOS DE PRUEBA PARA EMPRESA BOLIVIANA ===
-- Empresa: "Comercial Andina S.R.L." - La Paz, Bolivia
-- Giro: Venta de productos de consumo masivo y artículos de oficina

-- === 1. CONFIGURACIÓN BÁSICA ===

-- Niveles del plan de cuentas
INSERT INTO Nivel (nivel, digitos, descrip) VALUES
('1', 1, 'Nivel 1 - Grupos principales'),
('2', 2, 'Nivel 2 - Subgrupos'),
('3', 4, 'Nivel 3 - Cuentas de mayor'),
('4', 6, 'Nivel 4 - Subcuentas'),
('5', 8, 'Nivel 5 - Auxiliares');

-- Tipos de cuenta
INSERT INTO TipoCuenta (codigo, descrip) VALUES
('ACTIVO', 'Cuentas de Activo'),
('PASIVO', 'Cuentas de Pasivo'),
('PATRIMONIO', 'Cuentas de Patrimonio'),
('INGRESO', 'Cuentas de Ingreso'),
('EGRESO', 'Cuentas de Egreso'),
('ORDEN', 'Cuentas de Orden');

-- Movimientos de cuenta
INSERT INTO MovCuenta (codigo, descrip) VALUES
('DEUDOR', 'Saldo Deudor'),
('ACREEDOR', 'Saldo Acreedor'),
('AMBOS', 'Ambos movimientos');

-- Centros de costos
INSERT INTO CenCostos (codigo, descrip) VALUES
('VENTAS', 'Departamento de Ventas'),
('ADMIN', 'Administración'),
('ALMACEN', 'Almacén y Logística'),
('FINANC', 'Financiero'),
('MKTG', 'Marketing y Publicidad');

-- === 2. PLAN DE CUENTAS BÁSICO ===

-- ACTIVOS
INSERT INTO Plancuenta (cuenta, tipo_cuenta, nivel, descrip, tipomov, moneda, debebs, haberbs, usuario) VALUES
-- Activo Corriente
('1', 'ACTIVO', '1', 'ACTIVO', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('11', 'ACTIVO', '2', 'ACTIVO CORRIENTE', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('1101', 'ACTIVO', '3', 'CAJA Y BANCOS', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('110101', 'ACTIVO', '4', 'Caja General', 'DEUDOR', 'BOB', 15000, 0, 'admin'),
('110102', 'ACTIVO', '4', 'Caja Chica', 'DEUDOR', 'BOB', 2000, 0, 'admin'),
('110103', 'ACTIVO', '4', 'Banco Mercantil Santa Cruz', 'DEUDOR', 'BOB', 85000, 0, 'admin'),
('110104', 'ACTIVO', '4', 'Banco Nacional de Bolivia', 'DEUDOR', 'BOB', 45000, 0, 'admin'),
('110105', 'ACTIVO', '4', 'Banco Sol', 'DEUDOR', 'BOB', 25000, 0, 'admin'),

('1102', 'ACTIVO', '3', 'CUENTAS POR COBRAR', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('110201', 'ACTIVO', '4', 'Clientes Nacionales', 'DEUDOR', 'BOB', 75000, 0, 'admin'),
('110202', 'ACTIVO', '4', 'Documentos por Cobrar', 'DEUDOR', 'BOB', 35000, 0, 'admin'),
('110203', 'ACTIVO', '4', 'Anticipo a Proveedores', 'DEUDOR', 'BOB', 12000, 0, 'admin'),

('1103', 'ACTIVO', '3', 'INVENTARIOS', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('110301', 'ACTIVO', '4', 'Mercaderías', 'DEUDOR', 'BOB', 180000, 0, 'admin'),
('110302', 'ACTIVO', '4', 'Productos en Tránsito', 'DEUDOR', 'BOB', 25000, 0, 'admin'),

-- Activo No Corriente
('12', 'ACTIVO', '2', 'ACTIVO NO CORRIENTE', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('1201', 'ACTIVO', '3', 'BIENES DE USO', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('120101', 'ACTIVO', '4', 'Muebles y Enseres', 'DEUDOR', 'BOB', 45000, 0, 'admin'),
('120102', 'ACTIVO', '4', 'Equipos de Computación', 'DEUDOR', 'BOB', 28000, 0, 'admin'),
('120103', 'ACTIVO', '4', 'Vehículos', 'DEUDOR', 'BOB', 120000, 0, 'admin'),
('120104', 'ACTIVO', '4', 'Depreciación Acumulada', 'ACREEDOR', 'BOB', 0, 35000, 'admin'),

-- PASIVOS
('2', 'PASIVO', '1', 'PASIVO', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('21', 'PASIVO', '2', 'PASIVO CORRIENTE', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('2101', 'PASIVO', '3', 'CUENTAS POR PAGAR', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('210101', 'PASIVO', '4', 'Proveedores Nacionales', 'ACREEDOR', 'BOB', 0, 95000, 'admin'),
('210102', 'PASIVO', '4', 'Acreedores Varios', 'ACREEDOR', 'BOB', 0, 18000, 'admin'),

('2102', 'PASIVO', '3', 'OBLIGACIONES FISCALES', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('210201', 'PASIVO', '4', 'IVA por Pagar', 'ACREEDOR', 'BOB', 0, 15000, 'admin'),
('210202', 'PASIVO', '4', 'IT por Pagar', 'ACREEDOR', 'BOB', 0, 8000, 'admin'),
('210203', 'PASIVO', '4', 'Retenciones por Pagar', 'ACREEDOR', 'BOB', 0, 5000, 'admin'),

('2103', 'PASIVO', '3', 'OBLIGACIONES LABORALES', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('210301', 'PASIVO', '4', 'Sueldos por Pagar', 'ACREEDOR', 'BOB', 0, 25000, 'admin'),
('210302', 'PASIVO', '4', 'Aguinaldos por Pagar', 'ACREEDOR', 'BOB', 0, 20000, 'admin'),
('210303', 'PASIVO', '4', 'Aportes Patronales', 'ACREEDOR', 'BOB', 0, 12000, 'admin'),

-- PATRIMONIO
('3', 'PATRIMONIO', '1', 'PATRIMONIO', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('31', 'PATRIMONIO', '2', 'CAPITAL', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('3101', 'PATRIMONIO', '3', 'CAPITAL SOCIAL', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('310101', 'PATRIMONIO', '4', 'Capital Pagado', 'ACREEDOR', 'BOB', 0, 200000, 'admin'),
('310102', 'PATRIMONIO', '4', 'Reservas', 'ACREEDOR', 'BOB', 0, 50000, 'admin'),
('310103', 'PATRIMONIO', '4', 'Resultados Acumulados', 'ACREEDOR', 'BOB', 0, 75000, 'admin'),

-- INGRESOS
('4', 'INGRESO', '1', 'INGRESOS', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('41', 'INGRESO', '2', 'INGRESOS OPERACIONALES', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('4101', 'INGRESO', '3', 'VENTAS', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('410101', 'INGRESO', '4', 'Ventas Mercaderías', 'ACREEDOR', 'BOB', 0, 0, 'admin'),
('410102', 'INGRESO', '4', 'Descuentos en Ventas', 'DEUDOR', 'BOB', 0, 0, 'admin'),

-- EGRESOS
('5', 'EGRESO', '1', 'EGRESOS', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('51', 'EGRESO', '2', 'COSTO DE VENTAS', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('5101', 'EGRESO', '3', 'COSTO DE MERCADERÍAS', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('510101', 'EGRESO', '4', 'Costo de Mercaderías Vendidas', 'DEUDOR', 'BOB', 0, 0, 'admin'),

('52', 'EGRESO', '2', 'GASTOS OPERACIONALES', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('5201', 'EGRESO', '3', 'GASTOS DE ADMINISTRACIÓN', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520101', 'EGRESO', '4', 'Sueldos y Salarios', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520102', 'EGRESO', '4', 'Alquileres', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520103', 'EGRESO', '4', 'Servicios Básicos', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520104', 'EGRESO', '4', 'Papelería y Útiles', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520105', 'EGRESO', '4', 'Gasto Depreciación', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520106', 'EGRESO', '4', 'Provisión Aguinaldos', 'DEUDOR', 'BOB', 0, 0, 'admin'),

('5202', 'EGRESO', '3', 'GASTOS DE VENTA', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520201', 'EGRESO', '4', 'Publicidad', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520202', 'EGRESO', '4', 'Comisiones de Venta', 'DEUDOR', 'BOB', 0, 0, 'admin'),
('520203', 'EGRESO', '4', 'Gastos de Transporte', 'DEUDOR', 'BOB', 0, 0, 'admin');

-- === 3. PROVEEDORES ===

INSERT INTO proveedor (razon, nit, autorizacion, telf, celular, email, depto, domicilio, usuario) VALUES
('Distribuidora La Paz S.A.', '1234567890', 'AUT-001-2024', '2-2501234', '70123456', 'ventas@distribuidoralapaz.com', 'La Paz', 'Av. Buenos Aires #1234, Zona San Pedro', 'admin'),
('Comercial Boliviana Ltda.', '0987654321', 'AUT-002-2024', '2-2789012', '75987654', 'contacto@comercialboliviana.com', 'La Paz', 'Calle Comercio #567, Zona Central', 'admin'),
('Importadora Andina S.R.L.', '1122334455', 'AUT-003-2024', '2-2345678', '71234567', 'compras@importadoraandina.bo', 'La Paz', 'Av. Mariscal Santa Cruz #890', 'admin'),
('Papelería El Estudiante', '5566778899', 'AUT-004-2024', '2-2123456', '72345678', 'elestudiante@gmail.com', 'La Paz', 'Calle Sagárnaga #234, Zona Rosario', 'admin'),
('Limpieza Total Ltda.', '9988776655', 'AUT-005-2024', '2-2567890', '73456789', 'ventas@limpiezatotal.bo', 'La Paz', 'Av. 6 de Agosto #1567, Zona San Jorge', 'admin'),
('Electrodomésticos La Moderna', '1357902468', 'AUT-006-2024', '2-2901234', '74567890', 'moderna@electrodomesticos.com', 'La Paz', 'Av. Camacho #456, Zona Central', 'admin');

-- Contactos de proveedores
INSERT INTO Proveedor_contacto (id_proveedor, nombre, cargo, telf, celular, email, es_principal) VALUES
(1, 'Carlos Mamani', 'Gerente de Ventas', '2-2501234', '70123456', 'carlos.mamani@distribuidoralapaz.com', TRUE),
(1, 'Ana Quispe', 'Ejecutiva de Cuentas', '2-2501235', '70123457', 'ana.quispe@distribuidoralapaz.com', FALSE),
(2, 'Roberto Fernández', 'Director Comercial', '2-2789012', '75987654', 'roberto.fernandez@comercialboliviana.com', TRUE),
(3, 'María Condori', 'Jefe de Ventas', '2-2345678', '71234567', 'maria.condori@importadoraandina.bo', TRUE),
(4, 'Juan Pérez', 'Propietario', '2-2123456', '72345678', 'juan.perez@gmail.com', TRUE),
(5, 'Silvia Rojas', 'Gerente General', '2-2567890', '73456789', 'silvia.rojas@limpiezatotal.bo', TRUE),
(6, 'Pedro Vargas', 'Vendedor Senior', '2-2901234', '74567890', 'pedro.vargas@electrodomesticos.com', TRUE);

-- === 4. CLIENTES ===

INSERT INTO cliente (razon, nit, telf, celular, email, depto, domicilio, limite_credito, usuario) VALUES
('Supermercado El Baratillo', '2244668800', '2-2334455', '76543210', 'compras@elbaratillo.com', 'La Paz', 'Av. Landaeta #789, Zona Villa Fátima', 50000, 'admin'),
('Farmacia San Miguel', '1133557799', '2-2445566', '77654321', 'farmacia.sanmiguel@gmail.com', 'La Paz', 'Calle Murillo #123, Zona Centro', 25000, 'admin'),
('Librería Universitaria', '3344556677', '2-2556677', '78765432', 'ventas@libreriauniversitaria.bo', 'La Paz', 'Av. Estudiantes #456, Zona Universitaria', 35000, 'admin'),
('Consultorio Médico Dr. López', '4455667788', '2-2667788', '79876543', 'consultas@drlopez.com', 'La Paz', 'Av. 16 de Julio #890, Zona El Prado', 15000, 'admin'),
('Escuela Particular San José', '5566778899', '2-2778899', '70987654', 'administracion@sanjose.edu.bo', 'La Paz', 'Calle Jaén #234, Zona Rosario', 40000, 'admin'),
('Restaurante La Kantuta', '6677889900', '2-2889900', '71098765', 'contacto@lakantuta.com', 'La Paz', 'Av. Arce #567, Zona Sopocachi', 20000, 'admin'),
('Ferretería El Martillo', '7788990011', '2-2990011', '72109876', 'ferreteria.martillo@gmail.com', 'La Paz', 'Calle Max Paredes #890, Zona Max Paredes', 30000, 'admin'),
('Peluquería Estilo y Belleza', '8899001122', '2-2001122', '73210987', 'estiloybelleza@hotmail.com', 'La Paz', 'Av. Buenos Aires #123, Zona Miraflores', 10000, 'admin');

-- Contactos de clientes
INSERT INTO Cliente_contacto (id_cliente, nombre, cargo, telf, celular, email, es_principal) VALUES
(1, 'Luis Mamani', 'Encargado de Compras', '2-2334455', '76543210', 'luis.mamani@elbaratillo.com', TRUE),
(2, 'Rosa Choque', 'Farmacéutica', '2-2445566', '77654321', 'rosa.choque@gmail.com', TRUE),
(3, 'Miguel Torrez', 'Administrador', '2-2556677', '78765432', 'miguel.torrez@libreriauniversitaria.bo', TRUE),
(4, 'Dr. Fernando López', 'Médico', '2-2667788', '79876543', 'fernando.lopez@drlopez.com', TRUE),
(5, 'Hermana Carmen', 'Directora', '2-2778899', '70987654', 'hna.carmen@sanjose.edu.bo', TRUE),
(6, 'Alberto Gutierrez', 'Chef Propietario', '2-2889900', '71098765', 'alberto.gutierrez@lakantuta.com', TRUE),
(7, 'Ramiro Ticona', 'Propietario', '2-2990011', '72109876', 'ramiro.ticona@gmail.com', TRUE),
(8, 'Carla Mendoza', 'Propietaria', '2-2001122', '73210987', 'carla.mendoza@hotmail.com', TRUE);

-- === 5. TIPOS DE CAMBIO ===

-- Insertar tipos de cambio para los últimos 30 días
INSERT INTO Dolar (fecha, ufv, usuario) VALUES
('2024-12-01', 2.85436, 'admin'),
('2024-12-02', 2.85487, 'admin'),
('2024-12-03', 2.85538, 'admin'),
('2024-12-04', 2.85589, 'admin'),
('2024-12-05', 2.85640, 'admin'),
('2024-12-06', 2.85691, 'admin'),
('2024-12-07', 2.85742, 'admin'),
('2024-12-08', 2.85793, 'admin'),
('2024-12-09', 2.85844, 'admin'),
('2024-12-10', 2.85895, 'admin');

-- Tipos de cambio USD
INSERT INTO Dolar_det (moneda, fecha, compra, venta) VALUES
('USD', '2024-12-01', 6.86, 6.96),
('USD', '2024-12-02', 6.86, 6.96),
('USD', '2024-12-03', 6.86, 6.96),
('USD', '2024-12-04', 6.87, 6.97),
('USD', '2024-12-05', 6.87, 6.97),
('USD', '2024-12-06', 6.87, 6.97),
('USD', '2024-12-07', 6.88, 6.98),
('USD', '2024-12-08', 6.88, 6.98),
('USD', '2024-12-09', 6.88, 6.98),
('USD', '2024-12-10', 6.89, 6.99);

-- === 6. LIBRO DE COMPRAS (Noviembre 2024) ===

INSERT INTO LibroCompras (tipo_fac, fecha, nit, proveedor, factura, autorizacion, codigocontrol, importe, exento, ice, neto, iva, estado, usuario) VALUES
('FACTURA', '2024-11-15', '1234567890', 1, '00001234', 'AUT-001-2024', 'CC-001234', 11600.00, 0.00, 0.00, 10000.00, 1300.00, 'CONTABILIZADO', 'admin'),
('FACTURA', '2024-11-18', '0987654321', 2, '00005678', 'AUT-002-2024', 'CC-005678', 5800.00, 0.00, 0.00, 5000.00, 650.00, 'CONTABILIZADO', 'admin'),
('FACTURA', '2024-11-20', '1122334455', 3, '00009012', 'AUT-003-2024', 'CC-009012', 23200.00, 0.00, 0.00, 20000.00, 2600.00, 'CONTABILIZADO', 'admin'),
('FACTURA', '2024-11-22', '5566778899', 4, '00001111', 'AUT-004-2024', 'CC-001111', 3480.00, 0.00, 0.00, 3000.00, 390.00, 'CONTABILIZADO', 'admin'),
('FACTURA', '2024-11-25', '9988776655', 5, '00002222', 'AUT-005-2024', 'CC-002222', 6960.00, 0.00, 0.00, 6000.00, 780.00, 'CONTABILIZADO', 'admin'),
('FACTURA', '2024-11-28', '1357902468', 6, '00003333', 'AUT-006-2024', 'CC-003333', 17400.00, 0.00, 0.00, 15000.00, 1950.00, 'PENDIENTE', 'admin');

-- === 7. LIBRO DE VENTAS (Noviembre 2024) ===

INSERT INTO LibroVentas (fecha, nit, cliente, razonsocial, factura, autorizacion, importe, exento, ice, neto, iva, estado, usuario) VALUES
('2024-11-16', '2244668800', 1, 'Supermercado El Baratillo', '00000101', 'AUT-VTA-001', 14500.00, 0.00, 0.00, 12500.00, 1625.00, 'COBRADA', 'admin'),
('2024-11-19', '1133557799', 2, 'Farmacia San Miguel', '00000102', 'AUT-VTA-001', 8700.00, 0.00, 0.00, 7500.00, 975.00, 'COBRADA', 'admin'),
('2024-11-21', '3344556677', 3, 'Librería Universitaria', '00000103', 'AUT-VTA-001', 11600.00, 0.00, 0.00, 10000.00, 1300.00, 'EMITIDA', 'admin'),
('2024-11-23', '4455667788', 4, 'Consultorio Médico Dr. López', '00000104', 'AUT-VTA-001', 4350.00, 0.00, 0.00, 3750.00, 487.50, 'COBRADA', 'admin'),
('2024-11-26', '5566778899', 5, 'Escuela Particular San José', '00000105', 'AUT-VTA-001', 20300.00, 0.00, 0.00, 17500.00, 2275.00, 'EMITIDA', 'admin'),
('2024-11-29', '6677889900', 6, 'Restaurante La Kantuta', '00000106', 'AUT-VTA-001', 5800.00, 0.00, 0.00, 5000.00, 650.00, 'COBRADA', 'admin'),
('2024-11-30', '7788990011', 7, 'Ferretería El Martillo', '00000107', 'AUT-VTA-001', 8700.00, 0.00, 0.00, 7500.00, 975.00, 'EMITIDA', 'admin');

-- === 8. ASIENTOS CONTABLES DE EJEMPLO ===

INSERT INTO Asiento (codigo, tipo, glosa, fecha, estado, usuario) VALUES
('ASI-001', 'DIARIO', 'Compra de mercaderías según factura 00001234', '2024-11-15', 'CONFIRMADO', 'admin'),
('ASI-002', 'DIARIO', 'Venta de mercaderías según factura 00000101', '2024-11-16', 'CONFIRMADO', 'admin'),
('ASI-003', 'DIARIO', 'Pago de sueldos del mes de noviembre', '2024-11-30', 'CONFIRMADO', 'admin'),
('ASI-004', 'DIARIO', 'Pago de servicios básicos noviembre', '2024-11-30', 'CONFIRMADO', 'admin');

-- Detalles del asiento de compra
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-001', '110301', 10000.00, 0.00, 'ALMACEN', 'Compra mercaderías', 1),
('ASI-001', '210201', 1300.00, 0.00, 'ADMIN', 'IVA Crédito Fiscal', 2),
('ASI-001', '210101', 0.00, 11300.00, 'ADMIN', 'Por pagar a proveedor', 3);

-- Detalles del asiento de venta
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-002', '110201', 14500.00, 0.00, 'VENTAS', 'Por cobrar a cliente', 1),
('ASI-002', '410101', 0.00, 12500.00, 'VENTAS', 'Venta de mercaderías', 2),
('ASI-002', '210201', 0.00, 1625.00, 'ADMIN', 'IVA Débito Fiscal', 3),
('ASI-002', '510101', 8500.00, 0.00, 'VENTAS', 'Costo de venta', 4),
('ASI-002', '110301', 0.00, 8500.00, 'ALMACEN', 'Salida de inventario', 5);

-- Detalles del asiento de sueldos
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-003', '520101', 25000.00, 0.00, 'ADMIN', 'Sueldos noviembre', 1),
('ASI-003', '210301', 0.00, 22500.00, 'ADMIN', 'Sueldos líquidos', 2),
('ASI-003', '210303', 0.00, 2500.00, 'ADMIN', 'Descuentos laborales', 3);

-- Detalles del asiento de servicios básicos
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-004', '520103', 2500.00, 0.00, 'ADMIN', 'Servicios básicos', 1),
('ASI-004', '210201', 325.00, 0.00, 'ADMIN', 'IVA servicios', 2),
('ASI-004', '110103', 0.00, 2825.00, 'ADMIN', 'Pago con cheque', 3);

-- === 9. TEMPLATES DE ASIENTOS ===

INSERT INTO Asientotemplate (tipo, descrip, glosa, usuario) VALUES
('DIARIO', 'Compra de Mercaderías', 'Compra de mercaderías según factura #FACTURA#', 'admin'),
('DIARIO', 'Venta de Mercaderías', 'Venta de mercaderías según factura #FACTURA#', 'admin'),
('DIARIO', 'Pago de Sueldos', 'Pago de sueldos del mes de #MES#', 'admin'),
('DIARIO', 'Cobro a Cliente', 'Cobro a cliente #CLIENTE# según recibo #RECIBO#', 'admin'),
('DIARIO', 'Pago a Proveedor', 'Pago a proveedor #PROVEEDOR# según comprobante #COMPROBANTE#', 'admin');

-- Detalles de templates
INSERT INTO Asientotemplate_det (id_template, cuenta, referencia, cencostos, orden, es_debe) VALUES
-- Template 1: Compra de Mercaderías
(1, '110301', 'Mercaderías', 'ALMACEN', 1, TRUE),
(1, '210201', 'IVA Crédito Fiscal', 'ADMIN', 2, TRUE),
(1, '210101', 'Por pagar a proveedor', 'ADMIN', 3, FALSE),

-- Template 2: Venta de Mercaderías
(2, '110201', 'Por cobrar a cliente', 'VENTAS', 1, TRUE),
(2, '410101', 'Venta de mercaderías', 'VENTAS', 2, FALSE),
(2, '210201', 'IVA Débito Fiscal', 'ADMIN', 3, FALSE),
(2, '510101', 'Costo de venta', 'VENTAS', 4, TRUE),
(2, '110301', 'Salida de inventario', 'ALMACEN', 5, FALSE),

-- Template 3: Pago de Sueldos
(3, '520101', 'Sueldos del mes', 'ADMIN', 1, TRUE),
(3, '210301', 'Sueldos líquidos por pagar', 'ADMIN', 2, FALSE),
(3, '210303', 'Descuentos laborales', 'ADMIN', 3, FALSE);

-- === 10. PRESUPUESTO 2024 ===

INSERT INTO Presupuesto (cuenta, anio, moneda, total, observaciones, usuario) VALUES
('410101', 2024, 'BOB', 1200000.00, 'Presupuesto de ventas para el año 2024', 'admin'),
('520101', 2024, 'BOB', 300000.00, 'Presupuesto de sueldos y salarios 2024', 'admin'),
('520103', 2024, 'BOB', 36000.00, 'Presupuesto de servicios básicos 2024', 'admin'),
('520201', 2024, 'BOB', 60000.00, 'Presupuesto de publicidad 2024', 'admin');

-- Detalle mensual del presupuesto de ventas
INSERT INTO Presupuesto_det (id_presupuesto, mes, monto, observaciones) VALUES
(1, 1, 90000.00, 'Ventas enero - temporada baja'),
(1, 2, 95000.00, 'Ventas febrero'),
(1, 3, 110000.00, 'Ventas marzo - inicio año escolar'),
(1, 4, 100000.00, 'Ventas abril'),
(1, 5, 105000.00, 'Ventas mayo - día de la madre'),
(1, 6, 95000.00, 'Ventas junio'),
(1, 7, 85000.00, 'Ventas julio - vacaciones de invierno'),
(1, 8, 120000.00, 'Ventas agosto - inicio segundo semestre'),
(1, 9, 110000.00, 'Ventas septiembre'),
(1, 10, 105000.00, 'Ventas octubre'),
(1, 11, 130000.00, 'Ventas noviembre - fin de año'),
(1, 12, 155000.00, 'Ventas diciembre - navidad y año nuevo');

-- Detalle mensual del presupuesto de sueldos
INSERT INTO Presupuesto_det (id_presupuesto, mes, monto, observaciones) VALUES
(2, 1, 25000.00, 'Sueldos enero'),
(2, 2, 25000.00, 'Sueldos febrero'),
(2, 3, 25000.00, 'Sueldos marzo'),
(2, 4, 25000.00, 'Sueldos abril'),
(2, 5, 25000.00, 'Sueldos mayo'),
(2, 6, 25000.00, 'Sueldos junio'),
(2, 7, 50000.00, 'Sueldos julio + aguinaldo'),
(2, 8, 25000.00, 'Sueldos agosto'),
(2, 9, 25000.00, 'Sueldos septiembre'),
(2, 10, 25000.00, 'Sueldos octubre'),
(2, 11, 25000.00, 'Sueldos noviembre'),
(2, 12, 50000.00, 'Sueldos diciembre + aguinaldo');

-- === 11. MÁS ASIENTOS CONTABLES DE PRÁCTICA ===

-- Asientos adicionales para diciembre 2024
INSERT INTO Asiento (codigo, tipo, glosa, fecha, estado, usuario) VALUES
('ASI-005', 'DIARIO', 'Cobro a cliente Supermercado El Baratillo', '2024-12-01', 'CONFIRMADO', 'admin'),
('ASI-006', 'DIARIO', 'Pago a Distribuidora La Paz S.A.', '2024-12-02', 'CONFIRMADO', 'admin'),
('ASI-007', 'DIARIO', 'Compra de útiles de oficina', '2024-12-03', 'CONFIRMADO', 'admin'),
('ASI-008', 'DIARIO', 'Depreciación mensual de activos fijos', '2024-12-31', 'BORRADOR', 'admin'),
('ASI-009', 'DIARIO', 'Provisión para aguinaldos', '2024-12-31', 'BORRADOR', 'admin'),
('ASI-010', 'AJUSTE', 'Ajuste de inventario físico', '2024-12-31', 'BORRADOR', 'admin');

-- Detalles de cobro a cliente
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-005', '110103', 14500.00, 0.00, 'VENTAS', 'Cobro en efectivo', 1),
('ASI-005', '110201', 0.00, 14500.00, 'VENTAS', 'Cancelación cuenta por cobrar', 2);

-- Detalles de pago a proveedor
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-006', '210101', 11300.00, 0.00, 'ADMIN', 'Cancelación deuda proveedor', 1),
('ASI-006', '110103', 0.00, 11300.00, 'ADMIN', 'Pago con transferencia bancaria', 2);

-- Detalles de compra útiles de oficina
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-007', '520104', 1500.00, 0.00, 'ADMIN', 'Papelería y útiles', 1),
('ASI-007', '210201', 195.00, 0.00, 'ADMIN', 'IVA Crédito Fiscal', 2),
('ASI-007', '110101', 0.00, 1695.00, 'ADMIN', 'Pago en efectivo', 3);

-- Detalles de depreciación
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-008', '520105', 2500.00, 0.00, 'ADMIN', 'Gasto depreciación mensual', 1),
('ASI-008', '120104', 0.00, 2500.00, 'ADMIN', 'Depreciación acumulada', 2);

-- Detalles de provisión aguinaldos
INSERT INTO Asiento_det (cod_asiento, cuenta, debebs, haberbs, cencosto, referencia, orden) VALUES
('ASI-009', '520106', 20833.33, 0.00, 'ADMIN', 'Provisión aguinaldo (1/12)', 1),
('ASI-009', '210302', 0.00, 20833.33, 'ADMIN', 'Aguinaldos por pagar', 2);

-- === 12. DATOS ADICIONALES PARA PRÁCTICA ===

-- Más transacciones en Libro de Compras (Diciembre)
INSERT INTO LibroCompras (tipo_fac, fecha, nit, proveedor, factura, autorizacion, codigocontrol, importe, exento, ice, neto, iva, estado, usuario) VALUES
('FACTURA', '2024-12-05', '1234567890', 1, '00001235', 'AUT-001-2024', 'CC-001235', 8700.00, 0.00, 0.00, 7500.00, 975.00, 'CONTABILIZADO', 'admin'),
('FACTURA', '2024-12-08', '5566778899', 4, '00001112', 'AUT-004-2024', 'CC-001112', 1740.00, 0.00, 0.00, 1500.00, 195.00, 'CONTABILIZADO', 'admin'),
('NOTA_DEBITO', '2024-12-10', '0987654321', 2, 'ND-001', 'AUT-002-2024', 'CC-ND001', 580.00, 0.00, 0.00, 500.00, 65.00, 'PENDIENTE', 'admin'),
('RECIBO', '2024-12-12', '9988776655', 5, 'REC-001', 'AUT-005-2024', 'CC-REC001', 2320.00, 0.00, 0.00, 2000.00, 260.00, 'CONTABILIZADO', 'admin');

-- Más transacciones en Libro de Ventas (Diciembre)
INSERT INTO LibroVentas (fecha, nit, cliente, razonsocial, factura, autorizacion, importe, exento, ice, neto, iva, estado, usuario) VALUES
('2024-12-03', '8899001122', 8, 'Peluquería Estilo y Belleza', '00000108', 'AUT-VTA-001', 2900.00, 0.00, 0.00, 2500.00, 325.00, 'COBRADA', 'admin'),
('2024-12-06', '2244668800', 1, 'Supermercado El Baratillo', '00000109', 'AUT-VTA-001', 17400.00, 0.00, 0.00, 15000.00, 1950.00, 'EMITIDA', 'admin'),
('2024-12-09', '3344556677', 3, 'Librería Universitaria', '00000110', 'AUT-VTA-001', 8700.00, 0.00, 0.00, 7500.00, 975.00, 'COBRADA', 'admin'),
('2024-12-12', '6677889900', 6, 'Restaurante La Kantuta', '00000111', 'AUT-VTA-001', 11600.00, 0.00, 0.00, 10000.00, 1300.00, 'EMITIDA', 'admin');


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