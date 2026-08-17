from flask import Flask
from flask_mail import Mail
from app.core.config import settings

mail = Mail()

def init_mail(app: Flask):
    """
    Cấu hình và khởi tạo extension Flask-Mail cho ứng dụng Flask.
    """
    app.config.update(
        MAIL_SERVER=settings.mail_server,
        MAIL_PORT=settings.mail_port,
        MAIL_USE_TLS=settings.mail_use_tls,
        MAIL_USE_SSL=settings.mail_use_ssl,
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_DEFAULT_SENDER=settings.mail_default_sender,
    )
    if app.testing or app.config.get("TESTING", False):
        app.config["MAIL_SUPPRESS_SEND"] = True
    mail.init_app(app)