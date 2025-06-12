from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.auth.models import PasswordResetToken
from app.core.config import settings  
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()  # Load email settings from .env

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


# Token settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_reset_token(db: Session, user_id: int) -> str:
    token = str(uuid.uuid4())
    expiration = datetime.utcnow() + timedelta(minutes=15)
    reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expiration_time=expiration,
        used=False
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return token


# check if token is valid, unused and not expired
def verify_reset_token(db: Session, token: str) -> PasswordResetToken:
    record = db.query(PasswordResetToken).filter_by(token=token, used=False).first()
    if not record or record.expiration_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    return record


def mark_token_used(db: Session, token_record: PasswordResetToken):
    token_record.used = True
    db.commit()


# def send_reset_email(email: str, token: str) -> str:
#     reset_link = f"http://localhost:8000/auth/reset-password?token={token}"
#     print(f"[Email Sent to {email}]: {reset_link}")
#     return reset_link


def send_reset_email(email: str, token: str) -> str:

    print("EMAIL_FROM:", os.getenv("EMAIL_FROM"))
    print("EMAIL_PASSWORD:", os.getenv("EMAIL_PASSWORD"))
    print("SMTP_SERVER:", os.getenv("SMTP_SERVER"))
    print("SMTP_PORT:", os.getenv("SMTP_PORT"))
    reset_link = f"http://localhost:8000/auth/reset-password?token={token}"
    subject = "Reset Your Password"
    body = f"""
    Hi,

    You requested a password reset. Click the link below to reset your password:

    {reset_link}

    This link will expire in 15 minutes.

    If you didn't request this, please ignore this email.

    - Your App Team
    """

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = email
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reset email.")

    return reset_link