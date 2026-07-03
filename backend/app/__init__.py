from flask import Flask, g

from app.core.config import settings

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return '<h1>Hello, World!</h1>'
    
    # Cấu hình ứng dụng
    app.config['DEBUG'] = settings.debug

    # Đăng ký before_request 
    from app.core.hook import login_required
    
    app.before_request(login_required)


    # teardown db
    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop('db', None)
        if db is not None:
            if error:
                db.rollback()
            db.close()

    # Đăng ký blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app