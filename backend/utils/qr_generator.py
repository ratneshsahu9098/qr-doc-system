import qrcode
from io import BytesIO


def generate_qr_image(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    return img


def generate_qr_bytes(url):
    img = generate_qr_image(url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf
