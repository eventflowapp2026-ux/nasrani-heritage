import qrcode
from io import BytesIO
from django.core.files import File
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import tempfile
import os
from django.conf import settings

def generate_qr_code(data):
    """Generate QR code image and return as BytesIO"""
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer

def generate_pdf_with_qr(html_string, qr_code_url=None):
    """Generate PDF from HTML with QR code"""
    font_config = FontConfiguration()
    
    # Create PDF
    pdf_file = BytesIO()
    
    # Add QR code if provided
    if qr_code_url:
        # You might want to embed the QR code image
        pass
    
    HTML(string=html_string).write_pdf(
        pdf_file,
        font_config=font_config
    )
    
    pdf_file.seek(0)
    return pdf_file.read()

def create_slug(text):
    """Create URL-friendly slug from text"""
    from django.utils.text import slugify
    import re
    
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^\w\s-]', '', text.lower())
    
    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text

def send_notification_email(user, subject, message):
    """Send email notification to user"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )

def format_timestamp(timestamp):
    """Format timestamp for display"""
    from django.utils import timezone
    from django.contrib.humanize.templatetags.humanize import naturaltime
    
    return naturaltime(timestamp)

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
