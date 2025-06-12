from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
# from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth import models as auth_models
from app.core.database import get_db
from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
oauth2_scheme = HTTPBearer()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

SECRET_KEY = "your-secret-key"  # Use environment variable in production
ALGORITHM = "HS256"


# Get current authenticated user from token
def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        token_str = token.credentials
        print("Received token:", token_str)
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded payload:", payload)
        user_id: int = int(payload.get("sub"))
    except (JWTError, ValueError) as e:
        print("Token decode error:", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user = db.query(auth_models.User).filter(auth_models.User.id == user_id).first()
    if user is None:
        print("User not found in DB for ID:", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return user

# Admin-only access dependency
def admin_required(current_user: auth_models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

# User-only access dependency
def user_required(current_user: auth_models.User = Depends(get_current_user)):
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required",
        )
    return current_user
