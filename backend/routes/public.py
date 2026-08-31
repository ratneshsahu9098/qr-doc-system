from flask import Blueprint, render_template_string, jsonify
from backend.models.document import Document

public_bp = Blueprint('public', __name__)

DOCUMENT_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; }
        .header { background: #1a237e; color: white; padding: 20px; text-align: center; }
        .header h1 { font-size: 1.5rem; margin-bottom: 5px; }
        .header p { opacity: 0.8; font-size: 0.9rem; }
        .container { max-width: 900px; margin: 20px auto; padding: 0 15px; }
        .pdf-viewer { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .pdf-viewer iframe { width: 100%; height: 80vh; border: none; }
        .actions { padding: 15px; text-align: center; border-top: 1px solid #eee; }
        .btn { display: inline-block; padding: 10px 24px; background: #1a237e; color: white; text-decoration: none; border-radius: 6px; margin: 5px; font-size: 0.95rem; }
        .btn:hover { background: #283593; }
        .btn-outline { background: transparent; border: 2px solid #1a237e; color: #1a237e; }
        .btn-outline:hover { background: #1a237e; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        {% if description %}<p>{{ description }}</p>{% endif %}
    </div>
    <div class="container">
        <div class="pdf-viewer">
            <iframe src="{{ drive_url }}" title="{{ title }}"></iframe>
            <div class="actions">
                <a href="{{ drive_url }}" target="_blank" class="btn">Open in Drive</a>
                <a href="{{ drive_url }}" download class="btn btn-outline">Download PDF</a>
            </div>
        </div>
    </div>
</body>
</html>
"""


@public_bp.route('/<code>')
def view_document(code):
    doc = Document.query.filter_by(code=code).first_or_404()
    return render_template_string(
        DOCUMENT_PAGE_TEMPLATE,
        title=doc.title,
        description=doc.description,
        drive_url=doc.drive_url
    )


@public_bp.route('/<code>/json')
def view_document_json(code):
    doc = Document.query.filter_by(code=code).first_or_404()
    return jsonify(doc.to_dict())
