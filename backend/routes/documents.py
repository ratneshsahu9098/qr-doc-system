import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.models.db import db
from backend.models.document import Document
from backend.utils.code_generator import generate_document_code
from backend.services.drive import upload_pdf, delete_file, replace_file
import os

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('', methods=['GET'])
@jwt_required()
def list_documents():
    docs = Document.query.order_by(Document.created_at.desc()).all()
    return jsonify([d.to_dict() for d in docs])


@documents_bp.route('', methods=['POST'])
@jwt_required()
def create_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    title = request.form.get('title', file.filename)
    description = request.form.get('description', '')

    upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    temp_path = os.path.join(upload_dir, file.filename)
    file.save(temp_path)

    try:
        folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID', '')
        try:
            drive_result = upload_pdf(temp_path, file.filename, folder_id or None)
        except FileNotFoundError:
            return jsonify({'error': 'Google Drive credentials not configured. Place credentials.json in backend/ folder.'}), 503
        except Exception as e:
            return jsonify({'error': f'Google Drive error: {str(e)}'}), 500

        code = generate_document_code()
        while Document.query.filter_by(code=code).first():
            code = generate_document_code()

        doc = Document(
            code=code,
            title=title,
            description=description,
            drive_file_id=drive_result['file_id'],
            drive_url=drive_result['url']
        )
        db.session.add(doc)
        db.session.commit()
        return jsonify(doc.to_dict()), 201
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@documents_bp.route('/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return jsonify(doc.to_dict())


@documents_bp.route('/<int:doc_id>', methods=['PUT'])
@jwt_required()
def update_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    data = request.get_json()

    if data.get('title'):
        doc.title = data['title']
    if data.get('description') is not None:
        doc.description = data['description']

    db.session.commit()
    return jsonify(doc.to_dict())


@documents_bp.route('/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    delete_file(doc.drive_file_id)
    db.session.delete(doc)
    db.session.commit()
    return jsonify({'message': 'Document deleted'})


@documents_bp.route('/<int:doc_id>/replace', methods=['POST'])
@jwt_required()
def replace_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    temp_path = os.path.join(upload_dir, file.filename)
    file.save(temp_path)

    try:
        folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID', '')
        try:
            drive_result = replace_file(
                doc.drive_file_id, temp_path, file.filename, folder_id or None
            )
        except FileNotFoundError:
            return jsonify({'error': 'Google Drive credentials not configured.'}), 503
        except Exception as e:
            return jsonify({'error': f'Google Drive error: {str(e)}'}), 500

        doc.drive_file_id = drive_result['file_id']
        doc.drive_url = drive_result['url']

        if request.form.get('title'):
            doc.title = request.form['title']
        if request.form.get('description') is not None:
            doc.description = request.form['description']

        db.session.commit()
        return jsonify(doc.to_dict())
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
