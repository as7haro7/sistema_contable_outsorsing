CREATE TABLE TipoAsiento (
    codigo VARCHAR(50) PRIMARY KEY,
    descrip VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Nivel (
    nivel VARCHAR(50) PRIMARY KEY,
    digitos INTEGER NOT NULL CHECK (digitos > 0),
    descrip VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE MovCuenta (
    codigo VARCHAR(50) PRIMARY KEY,
    descrip VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE TipoCuenta (
    codigo VARCHAR(50) PRIMARY KEY,
    descrip VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE Moneda (
    codigo VARCHAR(50) PRIMARY KEY,
    descrip VARCHAR(255) NOT NULL,
    simbolo VARCHAR(10),
    activo BOOLEAN DEFAULT TRUE,
    es_moneda_base BOOLEAN DEFAULT FALSE
);

CREATE TABLE CenCostos (
    codigo VARCHAR(50) PRIMARY KEY,
    descrip VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === PLAN DE CUENTAS ===

CREATE TABLE Plancuenta (
    cuenta VARCHAR(100) PRIMARY KEY,
    tipo_cuenta VARCHAR(50) NOT NULL,
    nivel VARCHAR(50) NOT NULL,
    descrip VARCHAR(255) NOT NULL,
    tipomov VARCHAR(50) NOT NULL,
    moneda VARCHAR(50) NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    debebs NUMERIC(18, 2) DEFAULT 0.00,
    haberbs NUMERIC(18, 2) DEFAULT 0.00,
    debesus NUMERIC(18, 2) DEFAULT 0.00,
    habersus NUMERIC(18, 2) DEFAULT 0.00,
    activo BOOLEAN DEFAULT TRUE,
    usuario VARCHAR(50) NOT NULL,
    fechasys TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_plancuenta_tipocta FOREIGN KEY (tipo_cuenta) REFERENCES TipoCuenta(codigo) ON DELETE RESTRICT,
    CONSTRAINT fk_plancuenta_nivel FOREIGN KEY (nivel) REFERENCES Nivel(nivel) ON DELETE RESTRICT,
    CONSTRAINT fk_plancuenta_tipomov FOREIGN KEY (tipomov) REFERENCES MovCuenta(codigo) ON DELETE RESTRICT,
    CONSTRAINT fk_plancuenta_moneda FOREIGN KEY (moneda) REFERENCES Moneda(codigo) ON DELETE RESTRICT
);

-- === PROVEEDORES Y CLIENTES ===

CREATE TABLE proveedor (
    id SERIAL PRIMARY KEY,
    razon VARCHAR(255) NOT NULL,
    nit VARCHAR(50) UNIQUE,
    autorizacion VARCHAR(50),
    telf VARCHAR(50),
    celular VARCHAR(50),
    email VARCHAR(100),
    pais VARCHAR(50) DEFAULT 'Bolivia',
    depto VARCHAR(50),
    domicilio VARCHAR(255),
    creditobs VARCHAR(50),
    creditusus VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    usuario VARCHAR(50) NOT NULL,
    fechasys TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Proveedor_contacto (
    id SERIAL PRIMARY KEY,
    id_proveedor INTEGER NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    telf VARCHAR(50),
    celular VARCHAR(50),
    email VARCHAR(100),
    es_principal BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_proveedor_contacto_prov FOREIGN KEY (id_proveedor) REFERENCES proveedor(id) ON DELETE CASCADE
);

CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    razon VARCHAR(255) NOT NULL,
    nit VARCHAR(50) UNIQUE,
    telf VARCHAR(50),
    celular VARCHAR(50),
    email VARCHAR(100),
    pais VARCHAR(50) DEFAULT 'Bolivia',
    depto VARCHAR(50),
    domicilio VARCHAR(255),
    limite_credito NUMERIC(18, 2) DEFAULT 0.00,
    activo BOOLEAN DEFAULT TRUE,
    usuario VARCHAR(50) NOT NULL,
    fechasys TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Cliente_contacto (
    id SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    telf VARCHAR(50),
    celular VARCHAR(50),
    email VARCHAR(100),
    es_principal BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cliente_contacto_cli FOREIGN KEY (id_cliente) REFERENCES cliente(id) ON DELETE CASCADE
);

-- === ASIENTOS CONTABLES ===

CREATE TABLE Asiento (
    codigo VARCHAR(50) PRIMARY KEY,
    cta VARCHAR(100),
    tipo VARCHAR(50) NOT NULL,
    secuencia INTEGER DEFAULT 0,
    srs VARCHAR(50),
    debebs NUMERIC(18, 2) DEFAULT 0.00,
    haberbs NUMERIC(18, 2) DEFAULT 0.00,
    debesus NUMERIC(18, 2) DEFAULT 0.00,
    habersus NUMERIC(18, 2) DEFAULT 0.00,
    glosa VARCHAR(500) NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    estado VARCHAR(20) DEFAULT 'BORRADOR', -- BORRADOR, CONFIRMADO, ANULADO
    usuario VARCHAR(50) NOT NULL,
    fechasys TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_confirmacion VARCHAR(50),
    fecha_confirmacion TIMESTAMP,
    CONSTRAINT fk_asiento_tipo FOREIGN KEY (tipo) REFERENCES TipoAsiento(codigo) ON DELETE RESTRICT,
    CONSTRAINT fk_asiento_cuenta FOREIGN KEY (cta) REFERENCES Plancuenta(cuenta) ON DELETE SET NULL
);

CREATE TABLE Asiento_det (
    id SERIAL PRIMARY KEY,
    cod_asiento VARCHAR(50) NOT NULL,
    cuenta VARCHAR(100) NOT NULL,
    item VARCHAR(50),
    debebs NUMERIC(18, 2) DEFAULT 0.00,
    haberbs NUMERIC(18, 2) DEFAULT 0.00,
    debesus NUMERIC(18, 2) DEFAULT 0.00,
    habersus NUMERIC(18, 2) DEFAULT 0.00,
    cencosto VARCHAR(50),
    referencia VARCHAR(255),
    orden INTEGER DEFAULT 0,
    CONSTRAINT fk_asientodet_asiento FOREIGN KEY (cod_asiento) REFERENCES Asiento(codigo) ON DELETE CASCADE,
    CONSTRAINT fk_asientodet_plancuenta FOREIGN KEY (cuenta) REFERENCES Plancuenta(cuenta) ON DELETE RESTRICT,
    CONSTRAINT fk_asientodet_cencosto FOREIGN KEY (cencosto) REFERENCES CenCostos(codigo) ON DELETE SET NULL,
    CONSTRAINT chk_debe_haber CHECK ((debebs > 0 AND haberbs = 0) OR (debebs = 0 AND haberbs > 0) OR (debebs = 0 AND haberbs = 0))
);

-- === LIBROS DE COMPRAS Y VENTAS ===

CREATE TABLE LibroCompras (
    id SERIAL PRIMARY KEY,
    tipo_fac VARCHAR(50) NOT NULL DEFAULT 'FACTURA',
    poliza VARCHAR(50),
    fecha DATE NOT NULL,
    nit VARCHAR(50) NOT NULL,
    proveedor INTEGER NOT NULL,
    factura VARCHAR(50) NOT NULL,
    autorizacion VARCHAR(50),
    codigocontrol VARCHAR(50),
    importe NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    exento NUMERIC(18, 2) DEFAULT 0.00,
    ice NUMERIC(18, 2) DEFAULT 0.00,
    neto NUMERIC(18, 2) DEFAULT 0.00,
    iva NUMERIC(18, 2) DEFAULT 0.00,
    flete NUMERIC(18, 2) DEFAULT 0.00,
    asiento VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'PENDIENTE', -- PENDIENTE, CONTABILIZADO, ANULADO
    usuario VARCHAR(50) NOT NULL,
    fechasys TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_librocompras_prov FOREIGN KEY (proveedor) REFERENCES proveedor(id) ON DELETE RESTRICT,
    CONSTRAINT fk_librocompras_asiento FOREIGN KEY (asiento) REFERENCES Asiento(codigo) ON DELETE SET NULL,
    CONSTRAINT uk_compras_factura UNIQUE (proveedor, factura, autorizacion)
);

CREATE TABLE LibroVentas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    nit VARCHAR(50) NOT NULL,
    cliente INTEGER NOT NULL,
    razonsocial VARCHAR(255) NOT NULL,
    factura VARCHAR(50) NOT NULL,
    autorizacion VARCHAR(50) NOT NULL,
    importe NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    exento NUMERIC(18, 2) DEFAULT 0.00,
    ice NUMERIC(18, 2) DEFAULT 0.00,
    neto NUMERIC(18, 2) DEFAULT 0.00,
    iva NUMERIC(18, 2) DEFAULT 0.00,
    estado VARCHAR(50) DEFAULT 'EMITIDA', -- EMITIDA, COBRADA, ANULADA
    asiento VARCHAR(50),
    usuario VARCHAR(50) NOT NULL,
    fechasys TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_libroventas_cli FOREIGN KEY (cliente) REFERENCES cliente(id) ON DELETE RESTRICT,
    CONSTRAINT fk_libroventas_asiento FOREIGN KEY (asiento) REFERENCES Asiento(codigo) ON DELETE SET NULL,
    CONSTRAINT uk_ventas_factura UNIQUE (factura, autorizacion)
);

-- === TEMPLATES DE ASIENTOS ===

CREATE TABLE Asientotemplate (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    descrip VARCHAR(255) NOT NULL,
    glosa VARCHAR(500) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    usuario VARCHAR(50) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_asientotemplate_tipo FOREIGN KEY (tipo) REFERENCES TipoAsiento(codigo) ON DELETE RESTRICT
);

CREATE TABLE Asientotemplate_det (
    id SERIAL PRIMARY KEY,
    id_template INTEGER NOT NULL,
    cuenta VARCHAR(100) NOT NULL,
    item VARCHAR(50),
    referencia VARCHAR(255),
    cencostos VARCHAR(50),
    orden INTEGER DEFAULT 0,
    es_debe BOOLEAN DEFAULT TRUE, -- TRUE para debe, FALSE para haber
    CONSTRAINT fk_asientotemplatedet_tmpl FOREIGN KEY (id_template) REFERENCES Asientotemplate(id) ON DELETE CASCADE,
    CONSTRAINT fk_asientotemplatedet_cuenta FOREIGN KEY (cuenta) REFERENCES Plancuenta(cuenta) ON DELETE RESTRICT,
    CONSTRAINT fk_asientotemplatedet_cencos FOREIGN KEY (cencostos) REFERENCES CenCostos(codigo) ON DELETE SET NULL
);

-- === MONEDAS Y TIPOS DE CAMBIO ===

CREATE TABLE Dolar (
    fecha DATE PRIMARY KEY,
    ufv NUMERIC(18, 6) NOT NULL DEFAULT 0.000000,
    usuario VARCHAR(50) NOT NULL,
    fechasys TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Dolar_det (
    id SERIAL PRIMARY KEY,
    moneda VARCHAR(50) NOT NULL,
    fecha DATE NOT NULL,
    compra NUMERIC(18, 6) NOT NULL DEFAULT 0.000000,
    venta NUMERIC(18, 6) NOT NULL DEFAULT 0.000000,
    CONSTRAINT fk_dolardet_moneda FOREIGN KEY (moneda) REFERENCES Moneda(codigo) ON DELETE CASCADE,
    CONSTRAINT fk_dolardet_dolar FOREIGN KEY (fecha) REFERENCES Dolar(fecha) ON DELETE CASCADE,
    CONSTRAINT uk_moneda_fecha UNIQUE (moneda, fecha)
);

-- Agregar columna calculada después de crear la tabla
ALTER TABLE Dolar_det ADD COLUMN promedio NUMERIC(18, 6) GENERATED ALWAYS AS ((compra + venta) / 2) STORED;

-- === PRESUPUESTO ===

CREATE TABLE Presupuesto (
    id SERIAL PRIMARY KEY,
    cuenta VARCHAR(100) NOT NULL,
    anio INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    moneda VARCHAR(50) NOT NULL,
    total NUMERIC(18, 2) DEFAULT 0.00,
    observaciones TEXT,
    estado VARCHAR(20) DEFAULT 'ACTIVO', -- ACTIVO, CERRADO
    usuario VARCHAR(50) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_presupuesto_cuenta FOREIGN KEY (cuenta) REFERENCES Plancuenta(cuenta) ON DELETE RESTRICT,
    CONSTRAINT fk_presupuesto_moneda FOREIGN KEY (moneda) REFERENCES Moneda(codigo) ON DELETE RESTRICT,
    CONSTRAINT uk_presupuesto_cuenta_anio UNIQUE (cuenta, anio)
);

CREATE TABLE Presupuesto_det (
    id SERIAL PRIMARY KEY,
    id_presupuesto INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    monto NUMERIC(18, 2) DEFAULT 0.00,
    observaciones VARCHAR(255),
    CONSTRAINT fk_presupuestodet_pres FOREIGN KEY (id_presupuesto) REFERENCES Presupuesto(id) ON DELETE CASCADE,
    CONSTRAINT uk_presupuesto_mes UNIQUE (id_presupuesto, mes)
);









































































-- === ÍNDICES PARA MEJOR RENDIMIENTO ===

-- Índices para Proveedores
CREATE INDEX idx_proveedor_nit ON proveedor(nit);
CREATE INDEX idx_proveedor_razon ON proveedor(razon);
CREATE INDEX idx_proveedor_activo ON proveedor(activo);

-- Índices para Clientes
CREATE INDEX idx_cliente_nit ON cliente(nit);
CREATE INDEX idx_cliente_razon ON cliente(razon);
CREATE INDEX idx_cliente_activo ON cliente(activo);

-- Índices para Asientos
CREATE INDEX idx_asiento_fecha ON Asiento(fecha);
CREATE INDEX idx_asiento_tipo ON Asiento(tipo);
CREATE INDEX idx_asiento_estado ON Asiento(estado);
CREATE INDEX idx_asiento_usuario ON Asiento(usuario);

-- Índices para Detalles de Asientos
CREATE INDEX idx_asientodet_cuenta ON Asiento_det(cuenta);
CREATE INDEX idx_asientodet_cencosto ON Asiento_det(cencosto);

-- Índices para Libros
CREATE INDEX idx_librocompras_fecha ON LibroCompras(fecha);
CREATE INDEX idx_librocompras_proveedor ON LibroCompras(proveedor);
CREATE INDEX idx_librocompras_estado ON LibroCompras(estado);

CREATE INDEX idx_libroventas_fecha ON LibroVentas(fecha);
CREATE INDEX idx_libroventas_cliente ON LibroVentas(cliente);
CREATE INDEX idx_libroventas_estado ON LibroVentas(estado);

-- Índices para Plan de Cuentas
CREATE INDEX idx_plancuenta_tipo ON Plancuenta(tipo_cuenta);
CREATE INDEX idx_plancuenta_nivel ON Plancuenta(nivel);
CREATE INDEX idx_plancuenta_activo ON Plancuenta(activo);

-- === FUNCIONES Y TRIGGERS PARA AUDITORÍA ===

-- Función para actualizar fecha de modificación
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar fecha de modificación
CREATE TRIGGER trg_proveedor_update
    BEFORE UPDATE ON proveedor
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trg_cliente_update
    BEFORE UPDATE ON cliente
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trg_librocompras_update
    BEFORE UPDATE ON LibroCompras
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trg_libroventas_update
    BEFORE UPDATE ON LibroVentas
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- === VISTAS ===

-- Vista de saldos por cuenta
CREATE VIEW v_saldos_cuenta AS
SELECT 
    p.cuenta,
    p.descrip,
    p.tipo_cuenta,
    (p.debebs - p.haberbs) as saldo_bs,
    (p.debesus - p.habersus) as saldo_sus,
    p.moneda,
    p.activo
FROM Plancuenta p
WHERE p.activo = TRUE;

-- Vista de proveedores con contacto principal
CREATE VIEW v_proveedores_contacto AS
SELECT 
    p.id,
    p.razon,
    p.nit,
    p.telf,
    p.email,
    p.activo,
    pc.nombre as contacto_principal,
    pc.celular as contacto_celular
FROM proveedor p
LEFT JOIN Proveedor_contacto pc ON p.id = pc.id_proveedor AND pc.es_principal = TRUE
WHERE p.activo = TRUE;

-- Vista de clientes con contacto principal
CREATE VIEW v_clientes_contacto AS
SELECT 
    c.id,
    c.razon,
    c.nit,
    c.telf,
    c.email,
    c.activo,
    cc.nombre as contacto_principal,
    cc.celular as contacto_celular
FROM cliente c
LEFT JOIN Cliente_contacto cc ON c.id = cc.id_cliente AND cc.es_principal = TRUE
WHERE c.activo = TRUE;

-- Vista de libro de compras con datos del proveedor
CREATE VIEW v_libro_compras_completo AS
SELECT 
    lc.*,
    p.razon as razon_proveedor,
    p.email as email_proveedor
FROM LibroCompras lc
JOIN proveedor p ON lc.proveedor = p.id;

-- Vista de libro de ventas con datos del cliente
CREATE VIEW v_libro_ventas_completo AS
SELECT 
    lv.*,
    c.razon as razon_cliente,
    c.email as email_cliente
FROM LibroVentas lv
JOIN cliente c ON lv.cliente = c.id;

-- === COMENTARIOS EN TABLAS ===
COMMENT ON TABLE proveedor IS 'Tabla de proveedores de la empresa';
COMMENT ON TABLE cliente IS 'Tabla de clientes de la empresa';
COMMENT ON TABLE Asiento IS 'Asientos contables principales';
COMMENT ON TABLE Asiento_det IS 'Detalle de movimientos por asiento contable';
COMMENT ON TABLE LibroCompras IS 'Registro de compras para impuestos';
COMMENT ON TABLE LibroVentas IS 'Registro de ventas para impuestos';
COMMENT ON TABLE Plancuenta IS 'Plan de cuentas contable';

-- Ejemplo de datos iniciales básicos
INSERT INTO TipoAsiento (codigo, descrip) VALUES 
('DIARIO', 'Asiento de Diario'),
('APERTURA', 'Asiento de Apertura'),
('AJUSTE', 'Asiento de Ajuste'),
('CIERRE', 'Asiento de Cierre');

INSERT INTO Moneda (codigo, descrip, simbolo, es_moneda_base) VALUES 
('BOB', 'Bolivianos', 'Bs.', TRUE),
('USD', 'Dólares Americanos', '$', FALSE),
('EUR', 'Euros', '€', FALSE);