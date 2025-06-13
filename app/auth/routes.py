from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth import schemas
from app.auth.models import User
from app.auth.utils import hash_password, verify_password,create_access_token
from app.auth.utils import create_access_token 
from app.auth.models import PasswordResetToken
from app.auth.utils import (
    create_reset_token, verify_reset_token, mark_token_used, send_reset_email
)
from app.core.logger import logger

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=dict)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for email: {user.email}")
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        logger.warning(f"Signup failed: Email already registered - {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered.")
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")
    return {"message": "User registered successfully"}

@router.post("/signin", response_model=schemas.Token)
def signin(data: schemas.UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Signin attempt for email: {data.email}")
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        logger.warning(f"Signin failed: Invalid credentials for email - {data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    logger.info(f"User signed in: {user.email} (ID: {user.id})")
    return {"access_token": token, "token_type": "bearer"}


# reset and forgot password
@router.post("/forgot-password", response_model=dict)
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    logger.info(f"Password reset requested for email: {request.email}")
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        logger.warning(f"Password reset failed: User not found for email - {request.email}")
        raise HTTPException(status_code=404, detail="User not found")
   
    # geneate token and store in db
    token = create_reset_token(db, user.id)

    # send email to user with reset password
    send_reset_email(user.email, token)
    logger.info(f"Password reset token sent to: {user.email}")
    return {"message": "Password reset token sent to email."}

@router.post("/reset-password", response_model=dict)
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    logger.info("Attempting to reset password using token")
    token_record = verify_reset_token(db, request.token)
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        logger.error(f"Password reset failed: User not found for token {request.token}")
        raise HTTPException(status_code=404, detail="User not found")
    # update the user password 
    user.hashed_password = hash_password(request.new_password)
    
    # mark token as used 
    mark_token_used(db, token_record)
    db.commit()
    logger.info(f"Password successfully reset for user ID: {user.id}")
    return {"message": "Password has been reset successfully."}