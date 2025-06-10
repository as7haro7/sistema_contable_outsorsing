@echo off
REM Script para crear estructura de proyecto Flask para sistema contable

REM Definir la ruta base donde se creará el proyecto
set "basePath=%USERPROFILE%\Desktop\proyecto_contable"
if not exist "%basePath%" (
    mkdir "%basePath%"
)

REM Crear archivos raíz
type nul > "%basePath%\app.py"
type nul > "%basePath%\config.py"
type nul > "%basePath%\requirements.txt"
type nul > "%basePath%\run.py"

REM Crear estructura de carpetas
mkdir "%basePath%\controllers"
mkdir "%basePath%\models"
mkdir "%basePath%\templates\base"
mkdir "%basePath%\templates\auth"
mkdir "%basePath%\templates\dashboard"
mkdir "%basePath%\templates\empresas"
mkdir "%basePath%\templates\usuarios"
mkdir "%basePath%\templates\contabilidad\plancuentas"
mkdir "%basePath%\templates\contabilidad\asientos"
mkdir "%basePath%\templates\contabilidad\libros"
mkdir "%basePath%\templates\contabilidad\estados"
mkdir "%basePath%\templates\terceros\clientes"
mkdir "%basePath%\templates\terceros\proveedores"
mkdir "%basePath%\templates\iva"
mkdir "%basePath%\templates\reportes"
mkdir "%basePath%\templates\cliente_portal"
mkdir "%basePath%\static\material-dashboard\css"
mkdir "%basePath%\static\material-dashboard\js"
mkdir "%basePath%\static\material-dashboard\img"
mkdir "%basePath%\static\material-dashboard\fonts"
mkdir "%basePath%\static\custom\css"
mkdir "%basePath%\static\custom\js"
mkdir "%basePath%\static\uploads"
mkdir "%basePath%\utils"
mkdir "%basePath%\migrations"
mkdir "%basePath%\logs"

REM Crear archivos __init__.py
type nul > "%basePath%\controllers\__init__.py"
type nul > "%basePath%\models\__init__.py"
type nul > "%basePath%\utils\__init__.py"

REM Crear archivos de controladores
type nul > "%basePath%\controllers\auth_controller.py"
type nul > "%basePath%\controllers\dashboard_controller.py"
type nul > "%basePath%\controllers\empresas_controller.py"
type nul > "%basePath%\controllers\usuarios_controller.py"
type nul > "%basePath%\controllers\plancuentas_controller.py"
type nul > "%basePath%\controllers\asientos_controller.py"
type nul > "%basePath%\controllers\libros_controller.py"
type nul > "%basePath%\controllers\estados_controller.py"
type nul > "%basePath%\controllers\clientes_controller.py"
type nul > "%basePath%\controllers\proveedores_controller.py"
type nul > "%basePath%\controllers\iva_controller.py"
type nul > "%basePath%\controllers\reportes_controller.py"
type nul > "%basePath%\controllers\cliente_portal_controller.py"

REM Crear archivos de modelos
type nul > "%basePath%\models\database.py"
type nul > "%basePath%\models\auth_model.py"
type nul > "%basePath%\models\empresa_model.py"
type nul > "%basePath%\models\usuario_model.py"
type nul > "%basePath%\models\plancuenta_model.py"
type nul > "%basePath%\models\asiento_model.py"
type nul > "%basePath%\models\libro_model.py"
type nul > "%basePath%\models\estado_model.py"
type nul > "%basePath%\models\cliente_model.py"
type nul > "%basePath%\models\proveedor_model.py"
type nul > "%basePath%\models\iva_model.py"
type nul > "%basePath%\models\reporte_model.py"

REM Crear archivos de utilidades
type nul > "%basePath%\utils\decorators.py"
type nul > "%basePath%\utils\helpers.py"
type nul > "%basePath%\utils\validators.py"
type nul > "%basePath%\utils\pdf_generator.py"
type nul > "%basePath%\utils\excel_generator.py"
type nul > "%basePath%\utils\database_utils.py"

REM Crear archivos de migraciones
type nul > "%basePath%\migrations\create_master_db.sql"
type nul > "%basePath%\migrations\create_company_db.sql"

REM Crear archivos de logs
type nul > "%basePath%\logs\app.log"
type nul > "%basePath%\logs\error.log"

REM Crear archivos de templates
type nul > "%basePath%\templates\base\base.html"
type nul > "%basePath%\templates\base\sidebar.html"
type nul > "%basePath%\templates\base\navbar.html"
type nul > "%basePath%\templates\base\footer.html"
type nul > "%basePath%\templates\auth\login.html"
type nul > "%basePath%\templates\auth\select_empresa.html"
type nul > "%basePath%\templates\dashboard\index.html"
type nul > "%basePath%\templates\empresas\index.html"
type nul > "%basePath%\templates\empresas\create.html"
type nul > "%basePath%\templates\empresas\edit.html"
type nul > "%basePath%\templates\usuarios\index.html"
type nul > "%basePath%\templates\usuarios\create.html"
type nul > "%basePath%\templates\usuarios\edit.html"
type nul > "%basePath%\templates\contabilidad\plancuentas\index.html"
type nul > "%basePath%\templates\contabilidad\plancuentas\create.html"
type nul > "%basePath%\templates\contabilidad\plancuentas\edit.html"
type nul > "%basePath%\templates\contabilidad\asientos\index.html"
type nul > "%basePath%\templates\contabilidad\asientos\create.html"
type nul > "%basePath%\templates\contabilidad\asientos\edit.html"
type nul > "%basePath%\templates\contabilidad\asientos\view.html"
type nul > "%basePath%\templates\contabilidad\libros\diario.html"
type nul > "%basePath%\templates\contabilidad\libros\mayor.html"
type nul > "%basePath%\templates\contabilidad\estados\balance.html"
type nul > "%basePath%\templates\contabilidad\estados\resultados.html"
type nul > "%basePath%\templates\iva\compras.html"
type nul > "%basePath%\templates\iva\ventas.html"
type nul > "%basePath%\templates\reportes\index.html"
type nul > "%basePath%\templates\cliente_portal\dashboard.html"
type nul > "%basePath%\templates\cliente_portal\reportes.html"

REM Crear archivos static custom
type nul > "%basePath%\static\custom\css\custom.css"
type nul > "%basePath%\static\custom\js\contabilidad.js"
type nul > "%basePath%\static\custom\js\asientos.js"
type nul > "%basePath%\static\custom\js\plancuentas.js"

echo Estructura de proyecto creada exitosamente en: %basePath%
pause