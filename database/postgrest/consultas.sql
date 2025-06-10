-- CON BASE DE DATOS DE GESTION EMPRESARIAL
-- 1. Lista de usuarios y su(s) empresa(s) asignada(s)

SELECT 
    u.id AS usuario_id,
    u.username,
    u.nombre_completo,
    e.id AS empresa_id,
    e.razon_social
FROM usuarios u, usuario_empresas ue, empresas e
WHERE u.id = ue.usuario_id
  AND ue.empresa_id = e.id
  AND ue.activo = TRUE
ORDER BY u.username, e.razon_social;


-- 2. Gestiones activas por empresa
SELECT 
    g.id AS gestion_id,
    g.descripcion,
    g.periodo,
    e.razon_social
FROM gestiones g, empresas e
WHERE g.empresa_id = e.id
  AND g.activo = TRUE
ORDER BY e.razon_social, g.periodo DESC;


-- 3. Usuarios con su perfil y permisos (solo los activos)
SELECT 
    u.username,
    p.nombre AS perfil,
    pu.puede_crear,
    pu.puede_leer,
    pu.puede_actualizar,
    pu.puede_eliminar
FROM usuarios u, permisos_usuario pu, perfiles p
WHERE u.id = pu.usuario_id
  AND pu.perfil_id = p.id
  AND pu.activo = TRUE
ORDER BY u.username, p.nombre;


-- 4. Sesiones activas con nombre de usuario y empresa de contexto (si tiene)
SELECT 
    s.id AS sesion_id,
    u.username,
    e.razon_social AS empresa_contexto,
    s.fecha_inicio,
    s.fecha_expiracion
FROM sesiones s, usuarios u, empresas e
WHERE s.usuario_id = u.id
  AND s.empresa_contexto = e.id
  AND s.activa = TRUE
ORDER BY s.fecha_inicio DESC;



--- CON BASE DE DATOS DE CONTABILIDAD EMPRESA
-- 1. Lista de clientes activos con su correo y teléfono
SELECT 
    c.id, 
    c.razon, 
    c.nit, 
    c.email, 
    c.telf
FROM cliente c
WHERE c.activo = TRUE
ORDER BY c.razon;

-- 2. Proveedores con su contacto principal (si existe)
SELECT 
    p.id, 
    p.razon, 
    p.nit, 
    pc.nombre AS contacto_principal, 
    pc.celular
FROM proveedor p, Proveedor_contacto pc
WHERE p.id = pc.id_proveedor
  AND pc.es_principal = TRUE
  AND p.activo = TRUE
ORDER BY p.razon;

-- 3. Asientos contables con su glosa y total en Bs
SELECT 
    a.codigo, 
    a.fecha, 
    a.glosa, 
    a.debebs, 
    a.haberbs, 
    a.estado
FROM Asiento a
ORDER BY a.fecha DESC, a.codigo;

-- 4. Detalle de asientos con descripción de la cuenta
SELECT 
    ad.cod_asiento, 
    ad.cuenta, 
    pc.descrip AS descripcion_cuenta, 
    ad.debebs, 
    ad.haberbs
FROM Asiento_det ad, Plancuenta pc
WHERE ad.cuenta = pc.cuenta
ORDER BY ad.cod_asiento, ad.orden;

-- 5. Libro de ventas con nombre del cliente
SELECT 
    lv.id, 
    lv.fecha, 
    lv.factura, 
    lv.importe, 
    c.razon AS cliente
FROM LibroVentas lv, cliente c
WHERE lv.cliente = c.id
ORDER BY lv.fecha DESC, lv.id DESC;

-- 6. Presupuestos por cuenta con descripción y total
SELECT 
    p.id, 
    p.cuenta, 
    pc.descrip AS descripcion_cuenta, 
    p.anio, 
    p.total, 
    p.estado
FROM Presupuesto p, Plancuenta pc
WHERE p.cuenta = pc.cuenta
ORDER BY p.anio DESC, p.cuenta;