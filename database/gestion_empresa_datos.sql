-- =========================================================
-- DATOS DE PRUEBA CORREGIDOS - SISTEMA CONTABLE MULTIEMPRESA
-- =========================================================
-- NOTA: Este script asume que la extensión "pgcrypto" está habilitada
-- como se especifica en tu DDL (CREATE EXTENSION IF NOT EXISTS "pgcrypto").

-- === 1. USUARIOS ===
-- Se insertan primero los usuarios para que sus IDs puedan ser referenciadas después.
-- El campo 'supervisor_id' se actualizará al final para evitar problemas de dependencias.
-- Se añaden emails y se maneja la contraseña de forma segura.

INSERT INTO usuarios (username, nombre_completo, email, salt, password_hash, es_super_usuario, requiere_cambio_password) VALUES
('admin',     'Administrador del Sistema', 'admin@contasoft.com',   'salt_admin',   crypt('adminpass', gen_salt('bf')), TRUE,  FALSE),
('contador1', 'Carlos Mendoza Vargas',   'c.mendoza@contasoft.com', 'salt_c1',      crypt('contadorpass1', gen_salt('bf')), FALSE, TRUE),
('contador2', 'Patricia Rojas Silva',    'p.rojas@contasoft.com',   'salt_c2',      crypt('contadorpass2', gen_salt('bf')), FALSE, TRUE),
('cliente_lapaz', 'María Elena Quispe',  'me.quispe@cliente.com',   'salt_clp',     crypt('clientepass1', gen_salt('bf')),  FALSE, TRUE),
('cliente_norte', 'Roberto Fernández',   'r.fernandez@cliente.com', 'salt_cn',      crypt('clientepass2', gen_salt('bf')),  FALSE, TRUE),
('cliente_servicios','Ana Patricia López','ap.lopez@cliente.com',    'salt_cs',      crypt('clientepass3', gen_salt('bf')),  FALSE, TRUE);

-- Actualizar supervisores usando subconsultas para obtener los IDs correctos
UPDATE usuarios 
SET supervisor_id = (SELECT id FROM usuarios WHERE username = 'admin')
WHERE username IN ('contador1', 'contador2');

UPDATE usuarios 
SET supervisor_id = (SELECT id FROM usuarios WHERE username = 'contador1')
WHERE username IN ('cliente_lapaz', 'cliente_norte');

UPDATE usuarios 
SET supervisor_id = (SELECT id FROM usuarios WHERE username = 'contador2')
WHERE username = 'cliente_servicios';


-- === 2. EMPRESAS ===
-- Se corrigen los nombres de las columnas y se añaden los campos faltantes.

INSERT INTO empresas (razon_social, nit, representante_legal, telefono, celular, fax, email, website, pais, departamento, municipio, zona, direccion, usuario_creacion) VALUES
('CONTADORES ASOCIADOS S.R.L.', '1234567890', 'Carlos Mendoza Vargas', '44567890', '70123456', '44123456', 'contacto@contadores-asociados.com', 'www.contadores-asociados.com', 'Bolivia', 'Santa Cruz', 'Santa Cruz de la Sierra', 'Plan 3000', 'Av. Santos Dumont #234', 'admin'),
('COMERCIAL LA PAZ S.A.',       '2345678901', 'María Elena Quispe',    '22456789', '67891234', '22789012', 'contacto@comerciallapaz.com', 'www.comerciallapaz.com', 'Bolivia', 'La Paz', 'La Paz', 'Zona Sur', 'Av. Arce #1456', 'admin'),
('INDUSTRIAS DEL NORTE LTDA.',  '3456789012', 'Roberto Fernández',     '44678901', '78901234', '44234567', 'contacto@industriasnorte.com', 'www.industriasnorte.com', 'Bolivia', 'Santa Cruz', 'Santa Cruz de la Sierra', 'Norte', 'Radial 26 Km 8', 'admin'),
('SERVICIOS TÉCNICOS S.R.L.',   '4567890123', 'Ana Patricia López',    '44789012', '69012345', '44345678', 'contacto@serviciostecnicos.com', NULL, 'Bolivia', 'Santa Cruz', 'Santa Cruz de la Sierra', 'Centro', 'Calle Libertad #89', 'admin');


-- === 3. GESTIONES ===
-- Se utilizan subconsultas para asignar la 'empresa_id' correcta y se ajustan los nombres de las columnas.

INSERT INTO gestiones (empresa_id, descripcion, periodo, fecha_inicio, fecha_fin, nombre_base_datos, codigo_moneda, usuario_creacion) VALUES
((SELECT id FROM empresas WHERE nit = '2345678901'), 'Gestión 2024 - Comercial La Paz',     '2024', '2024-01-01', '2024-12-31', 'BD_CLP_2024', 'BOB', 'admin'),
((SELECT id FROM empresas WHERE nit = '3456789012'), 'Gestión 2024 - Industrias del Norte', '2024', '2024-01-01', '2024-12-31', 'BD_IDN_2024', 'BOB', 'admin'),
((SELECT id FROM empresas WHERE nit = '4567890123'), 'Gestión 2024 - Servicios Técnicos',   '2024', '2024-01-01', '2024-12-31', 'BD_STS_2024', 'BOB', 'admin');


-- === 4. ASIGNACIÓN USUARIO <-> EMPRESA ===
-- Se usan subconsultas para las IDs de usuario y empresa. Se define un rol explícito.

INSERT INTO usuario_empresas (usuario_id, empresa_id, rol, asignado_por) VALUES
((SELECT id FROM usuarios WHERE username = 'admin'),     (SELECT id FROM empresas WHERE nit = '1234567890'), 'ADMIN',    (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'contador1'), (SELECT id FROM empresas WHERE nit = '1234567890'), 'CONTADOR', (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'contador2'), (SELECT id FROM empresas WHERE nit = '1234567890'), 'CONTADOR', (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'cliente_lapaz'), (SELECT id FROM empresas WHERE nit = '2345678901'), 'CONSULTOR',(SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'cliente_norte'), (SELECT id FROM empresas WHERE nit = '3456789012'), 'CONSULTOR',(SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'cliente_servicios'), (SELECT id FROM empresas WHERE nit = '4567890123'), 'CONSULTOR',(SELECT id FROM usuarios WHERE username = 'admin'));


-- === 5. ASIGNACIÓN USUARIO <-> GESTIÓN ===
-- Se mapean los modos 'E' a 'ESCRITURA' y 'L' a 'LECTURA' y se usan subconsultas.

INSERT INTO usuario_gestiones (usuario_id, gestion_id, nivel_acceso, asignado_por) VALUES
((SELECT id FROM usuarios WHERE username = 'admin'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Comercial La Paz'), 'ADMINISTRADOR', (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'admin'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Industrias del Norte'), 'ADMINISTRADOR', (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'admin'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Servicios Técnicos'), 'ADMINISTRADOR', (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'contador1'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Comercial La Paz'), 'ESCRITURA', (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'contador1'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Industrias del Norte'), 'ESCRITURA', (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'contador2'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Servicios Técnicos'), 'ESCRITURA', (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'cliente_lapaz'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Comercial La Paz'), 'LECTURA', (SELECT id FROM usuarios WHERE username = 'contador1')),
((SELECT id FROM usuarios WHERE username = 'cliente_norte'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Industrias del Norte'), 'LECTURA', (SELECT id FROM usuarios WHERE username = 'contador1')),
((SELECT id FROM usuarios WHERE username = 'cliente_servicios'), (SELECT id FROM gestiones WHERE descripcion = 'Gestión 2024 - Servicios Técnicos'), 'LECTURA', (SELECT id FROM usuarios WHERE username = 'contador2'));


-- === 6. PERFILES DEL SISTEMA ===
-- Se corrigen los nombres de las columnas.

INSERT INTO perfiles (codigo, nombre, descripcion, ruta, es_menu, usuario_creacion) VALUES
('ADMIN',    'Administrador General', 'Acceso total al sistema y configuración.',        '/admin',    TRUE, 'admin'),
('CONTADOR', 'Contador Público',      'Acceso a módulos de contabilidad y reportes.',      '/contador', TRUE, 'admin'),
('CONSULTOR','Cliente - Solo Consulta', 'Acceso de solo lectura a reportes y estados.',    '/cliente',  TRUE, 'admin'),
('ASISTENTE','Asistente Contable',    'Acceso para registro de transacciones y tareas básicas.', '/asistente',TRUE, 'admin');


-- === 7. PERMISOS DE USUARIO ===
-- Se cambia el nombre de la tabla a 'permisos_usuario', se usan subconsultas y valores BOOLEAN.

INSERT INTO permisos_usuario (usuario_id, perfil_id, puede_crear, puede_actualizar, puede_eliminar, puede_imprimir, puede_exportar, asignado_por) VALUES
((SELECT id FROM usuarios WHERE username = 'admin'), (SELECT id FROM perfiles WHERE codigo = 'ADMIN'), TRUE, TRUE, TRUE, TRUE, TRUE, (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'contador1'), (SELECT id FROM perfiles WHERE codigo = 'CONTADOR'), TRUE, TRUE, TRUE, TRUE, TRUE, (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'contador2'), (SELECT id FROM perfiles WHERE codigo = 'CONTADOR'), TRUE, TRUE, TRUE, TRUE, TRUE, (SELECT id FROM usuarios WHERE username = 'admin')),
((SELECT id FROM usuarios WHERE username = 'cliente_lapaz'), (SELECT id FROM perfiles WHERE codigo = 'CONSULTOR'), FALSE, FALSE, FALSE, TRUE, TRUE, (SELECT id FROM usuarios WHERE username = 'contador1')),
((SELECT id FROM usuarios WHERE username = 'cliente_norte'), (SELECT id FROM perfiles WHERE codigo = 'CONSULTOR'), FALSE, FALSE, FALSE, TRUE, TRUE, (SELECT id FROM usuarios WHERE username = 'contador1')),
((SELECT id FROM usuarios WHERE username = 'cliente_servicios'),(SELECT id FROM perfiles WHERE codigo = 'CONSULTOR'), FALSE, FALSE, FALSE, TRUE, TRUE, (SELECT id FROM usuarios WHERE username = 'contador2'));



-- importante
INSERT INTO public.gestiones(
    id, uuid, empresa_id, descripcion, periodo, fecha_inicio, fecha_fin, nombre_base_datos, codigo_moneda, nombre_moneda, activo, cerrada, fecha_cierre, fecha_registro, fecha_actualizacion, usuario_creacion, usuario_actualizacion)
VALUES (4, uuid_generate_v4(), 1, 'Gestión 2025', '2025', '2025-01-01', '2025-12-31', 'contabilidad_emp_1_2025', 'BOB', 'Boliviano', TRUE, FALSE, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'admin', 'admin');