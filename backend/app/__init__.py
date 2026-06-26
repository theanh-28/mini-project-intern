from flask import Flask, g
from app.core.config import settings

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return '<h1>Hello, World!</h1>'
    
    # Cấu hình ứng dụng
    app.config['DEBUG'] = settings.debug

    
    # teardown db
    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop('db', None)
        if db is not None:
            if error:
                db.rollback()
            db.close()

    # Đăng ký blueprints


    return app