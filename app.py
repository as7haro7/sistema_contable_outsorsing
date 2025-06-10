from flask import Flask, redirect, url_for
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    from controllers.auth_controller import auth_bp
    from controllers.dashboard_controller import dashboard_bp
    from controllers.empresas_controller import empresas_bp
    from controllers.usuarios_controller import usuarios_bp
    from controllers.plancuentas_controller import plancuentas_bp
    from controllers.asientos_controller import asientos_bp
    from controllers.libros_controller import libros_bp
    from controllers.estados_controller import estados_bp
    from controllers.clientes_controller import clientes_bp
    from controllers.reportes_controller import reportes_bp
    from controllers.iva_controller import iva_bp
    from controllers.periodos_controller import periodos_bp
    from controllers.terceros_controller import terceros_bp
    from controllers.factura_controller import facturas_bp
    from controllers.configuracion_controller import configuracion_bp
    from controllers.descargas_controller import descargas_bp
    from controllers.gestiones_controller import gestiones_bp

    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(empresas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(plancuentas_bp)
    app.register_blueprint(asientos_bp)
    app.register_blueprint(libros_bp)
    app.register_blueprint(estados_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(iva_bp)
    app.register_blueprint(periodos_bp)
    app.register_blueprint(terceros_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(configuracion_bp)
    app.register_blueprint(descargas_bp)
    app.register_blueprint(gestiones_bp)


    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True,port=5151)


