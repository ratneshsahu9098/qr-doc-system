import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import config
from backend.models.db import db


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    app.config.from_object(config[config_name])

    db.init_app(app)
    CORS(app)
    JWTManager(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        db.create_all()

    from backend.routes.auth import auth_bp
    from backend.routes.documents import documents_bp
    from backend.routes.qr import qr_bp
    from backend.routes.public import public_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(qr_bp, url_prefix='/api/qr')
    app.register_blueprint(public_bp, url_prefix='/d')

    @app.route('/api')
    def api_info():
        return jsonify({
            'name': 'QR Document System API',
            'version': '1.0.0',
            'endpoints': {
                'login': 'POST /api/auth/login',
                'documents': 'GET/POST /api/documents',
                'qr': 'GET /api/qr/<doc_id>',
                'public': 'GET /d/<code>'
            }
        })

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        file_path = os.path.join(app.static_folder, path)
        if os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
