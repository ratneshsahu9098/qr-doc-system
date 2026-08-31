from flask import Blueprint, send_file, current_app
from backend.models.document import Document
from backend.utils.qr_generator import generate_qr_bytes

qr_bp = Blueprint('qr', __name__)


@qr_bp.route('/<int:doc_id>', methods=['GET'])
def get_qr(doc_id):
    doc = Document.query.get_or_404(doc_id)
    base_url = current_app.config.get('QR_BASE_URL', 'http://localhost:5000/d')
    url = f'{base_url}/{doc.code}'
    qr_buf = generate_qr_bytes(url)
    return send_file(qr_buf, mimetype='image/png', download_name=f'qr_{doc.code}.png')


@qr_bp.route('/code/<code>', methods=['GET'])
def get_qr_by_code(code):
    doc = Document.query.filter_by(code=code).first_or_404()
    base_url = current_app.config.get('QR_BASE_URL', 'http://localhost:5000/d')
    url = f'{base_url}/{doc.code}'
    qr_buf = generate_qr_bytes(url)
    return send_file(qr_buf, mimetype='image/png', download_name=f'qr_{doc.code}.png')
