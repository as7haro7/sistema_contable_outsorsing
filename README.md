✅ Resumen General del Proyecto – Sistema de Gestión Contable Web

1.  🎯 Propósito General

    Desarrollar una aplicación web para la gestión contable multiempresa orientada a empresas de outsourcing contable.

    Centralizar la gestión de:

        Plan contable

        Transacciones financieras

        Reportes legales y administrativos

    Integrar usuarios internos (contadores/administradores) y externos (clientes) con distintos niveles de acceso.

2.  🔑 Funcionalidades Clave

    Autenticación y control de accesos por rol

    Gestión multiempresa con separación de bases de datos

    Selector de empresa y gestión (cambio de contexto contable)

    Plan de Cuentas contable estructurado por niveles

    Registro y gestión de Asientos Contables

    Generación y consulta de:

        Libro Diario

        Libro Mayor

        Hoja de Trabajo

        Estados Financieros: Balance General, Estado de Resultados

    Gestión de Clientes y Proveedores

    Registro de facturas con cálculo automático de IVA

    Generación de Libros de Compras y Ventas (IVA)

    Exportación de reportes (PDF/Excel)

    Configuración general y backups

    Módulo Cliente (lectura de reportes)

3.  🧱 Arquitectura del Sistema: Modelo-Vista-Controlador (MVC)
    Modelo:

        Funciones que interactúan directamente con postgrest

        Separadas por entidad (usuarios.py, empresas.py, cuentas.py, etc.)

        Sin uso de ORM, consultas SQL manuales y funciones utilitarias

        Opcional: clases DTO para agrupar datos

Vista (HTML/CSS + Jinja2):

    Basadas en un template de administración (como AdminLTE, CoreUI, SB Admin)

    Componentes dinámicos usando Jinja2

    Soporte para menús según tipo de usuario

Controlador (Flask routes):

    Archivos organizados por módulo: usuarios_controller.py, asientos_controller.py, etc.

    Encargado de recibir peticiones, consultar el modelo y enviar los datos a la vista

4.  🧩 Componentes Principales y Módulos Detallados
    a) Gestión de Usuarios y Roles

        Login con sesión

        CRUD de usuarios y roles

        Permisos por módulo

b) Gestión de Empresas y Períodos Contables

    CRUD de empresas

    Selección de empresa y gestión activa

    Creación automática de base de datos por empresa

c) Plan de Cuentas

    Árbol jerárquico visual

    CRUD de cuentas por nivel

d) Asientos Contables

    Registro de transacciones

    Validación de partidas dobles (debe = haber)

    Consulta de asientos con filtros

e) Libros Contables

    Libro Diario

    Libro Mayor

    Exportación

f) Hoja de Trabajo

    Visualización de saldos

    Registro de ajustes

g) Estados Financieros

    Balance de Comprobación

    Balance General

    Estado de Resultados

h) Clientes y Proveedores

    CRUD de terceros

    Uso en facturas

i) IVA Compras/Ventas

    Registro de facturas con NIT y montos

    Generación automática de libro IVA

j) Reportes

    Selección de tipo y periodo

    Exportación a PDF / Excel

k) Módulo Cliente (solo lectura)

    Visualización de reportes generados

    Filtros por período

    Descarga de archivos

5.  🧰 Tecnologías y Herramientas
    Backend

        Python 3

        Flask

        postgrest

Frontend

    HTML5 + CSS3

    JavaScript (Bootstrap + JS básico)

    Jinja2

Base de Datos

    POSTGREST

    Estructura separada por empresa (BD_CONTABILIDAD_EMPRESA_X)

    BD maestra (BD_GESTION_EMPRESARIAL) para usuarios, empresas y configuraciones globales

6.  🔁 Flujo de Trabajo General (MVC)

    Usuario realiza acción en el navegador (Vista).

    Vista envía solicitud al Controlador (@app.route).

    Controlador procesa la lógica y consulta al Modelo.

    Modelo ejecuta las consultas SQL necesarias.

    Modelo retorna los datos al Controlador.

    Controlador pasa los datos a la Vista.

    Vista muestra los resultados al usuario.

7.  🔒 Gestión de Seguridad y Accesos

    Middleware para proteger rutas según roles

    Validación de sesión y permisos

    Trazabilidad: logs de actividad contable (opcional)

8.  📦 Extras a considerar (opcional pero recomendable)

        Backups y restauración por empresa

        Módulo de notificaciones (pendiente de ajustes, cierre, etc.)

        Soporte multilenguaje (ES/EN)

        Tareas programadas (por ejemplo, cierre mensual automático)



        Estructura de archivos:
        ├── app.py                          # Aplicación principal Flask

    ├── config.py # Configuraciones
    ├── requirements.txt # Dependencias
    ├── run.py # Script de inicio
    │
    ├── controllers/ # Controladores (Rutas Flask)
    │ ├── **init**.py
    │ ├── auth_controller.py # Login/Logout/Sesiones
    │ ├── dashboard_controller.py # Dashboard principal
    │ ├── empresas_controller.py # Gestión de empresas
    │ ├── usuarios_controller.py # CRUD usuarios
    │ ├── plancuentas_controller.py # Plan de cuentas
    │ ├── asientos_controller.py # Asientos contables
    │ ├── libros_controller.py # Libros contables
    │ ├── estados_controller.py # Estados financieros
    │ ├── clientes_controller.py # Gestión clientes
    │ ├── proveedores_controller.py # Gestión proveedores
    │ ├── iva_controller.py # IVA compras/ventas
    │ ├── reportes_controller.py # Generación reportes
    │ └── cliente_portal_controller.py # Portal para clientes
    │
    ├── models/ # Modelos (Lógica de datos)
    │ ├── **init**.py
    │ ├── database.py # Conexión PostgreSQL
    │ ├── auth_model.py # Autenticación
    │ ├── empresa_model.py # Empresas y gestiones
    │ ├── usuario_model.py # Usuarios y permisos
    │ ├── plancuenta_model.py # Plan de cuentas
    │ ├── asiento_model.py # Asientos contables
    │ ├── libro_model.py # Libros contables
    │ ├── estado_model.py # Estados financieros
    │ ├── cliente_model.py # Clientes
    │ ├── proveedor_model.py # Proveedores
    │ ├── iva_model.py # IVA
    │ └── reporte_model.py # Reportes
    │
    ├── templates/ # Vistas HTML (Jinja2)
    │ ├── base/
    │ │ ├── base.html # Template base
    │ │ ├── sidebar.html # Menú lateral
    │ │ ├── navbar.html # Barra superior
    │ │ └── footer.html # Pie de página
    │ ├── auth/
    │ │ ├── login.html # Página de login
    │ │ └── select_empresa.html # Selector de empresa
    │ ├── dashboard/
    │ │ └── index.html # Dashboard principal
    │ ├── empresas/
    │ │ ├── index.html # Lista empresas
    │ │ ├── create.html # Crear empresa
    │ │ └── edit.html # Editar empresa
    │ ├── usuarios/
    │ │ ├── index.html
    │ │ ├── create.html
    │ │ └── edit.html
    │ ├── contabilidad/
    │ │ ├── plancuentas/
    │ │ │ ├── index.html # Plan de cuentas
    │ │ │ ├── create.html # Nueva cuenta
    │ │ │ └── edit.html # Editar cuenta
    │ │ ├── asientos/
    │ │ │ ├── index.html # Lista asientos
    │ │ │ ├── create.html # Nuevo asiento
    │ │ │ ├── edit.html # Editar asiento
    │ │ │ └── view.html # Ver asiento
    │ │ ├── libros/
    │ │ │ ├── diario.html # Libro diario
    │ │ │ └── mayor.html # Libro mayor
    │ │ └── estados/
    │ │ ├── balance.html # Balance general
    │ │ └── resultados.html # Estado resultados
    │ ├── terceros/
    │ │ ├── clientes/
    │ │ └── proveedores/
    │ ├── iva/
    │ │ ├── compras.html
    │ │ └── ventas.html
    │ ├── reportes/
    │ │ └── index.html
    │ └── cliente_portal/
    │ ├── dashboard.html
    │ └── reportes.html
    │
    ├── static/ # Archivos estáticos
    │ ├── material-dashboard/ # Material Dashboard assets
    │ │ ├── css/
    │ │ ├── js/
    │ │ ├── img/
    │ │ └── fonts/
    │ ├── custom/
    │ │ ├── css/
    │ │ │ └── custom.css # Estilos personalizados
    │ │ └── js/
    │ │ ├── contabilidad.js # JS específico contabilidad
    │ │ ├── asientos.js # JS manejo asientos
    │ │ └── plancuentas.js # JS plan de cuentas
    │ └── uploads/ # Archivos subidos
    │
    ├── utils/ # Utilidades
    │ ├── **init**.py
    │ ├── decorators.py # Decoradores (auth, permisos)
    │ ├── helpers.py # Funciones auxiliares
    │ ├── validators.py # Validaciones
    │ ├── pdf_generator.py # Generador PDFs
    │ ├── excel_generator.py # Generador Excel
    │ └── database_utils.py # Utilidades BD
    │
    ├── migrations/ # Scripts de BD
    │ ├── create_master_db.sql # BD maestra
    │ └── create_company_db.sql # Template BD empresa
    │
    └── logs/ # Logs del sistema
    ├── app.log
    └── error.log
