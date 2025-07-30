"""
MFA utilities and helpers
"""
import qrcode
import io
import base64
from PIL import Image, ImageDraw


def generate_qr_code(uri):
    """Generate QR code for MFA setup"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def verify_mfa_token(secret, token):
    """Verify MFA token"""
    import pyotp
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)