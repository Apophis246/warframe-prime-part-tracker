# auth.py — outline only, no implementation yet.
#
# Handles the two unauthenticated routes plus the shared logic every
# other route depends on for knowing "who is making this request."
#
# Packages (already in requirements.txt — rebuild the image if you
# haven't since they were added):
#   pwdlib[argon2]  -> password hashing
#   pyjwt           -> token creation/verification

import jwt
import os

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .schemas import UserCreate, UserLogin, Token

password_hash = PasswordHash.recommended()
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
TOKEN_LIFETIME_MINUTES = 60




# --- POST /auth/register ------------------------------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def user_register(new_user: UserCreate, db: Session=Depends(get_db)):
    """
    Registers a new user and ensures that the input email or username is unique
    """
    existing_username = db.scalar(select(User).where(User.username == new_user.username))
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    existing_email = db.scalar(select(User).where(User.email == new_user.email))
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already taken")
    
    hashed = password_hash.hash(new_user.password)
    new_user_row = User(username=new_user.username, email=new_user.email, password_hash=hashed)
    db.add(new_user_row)
    db.commit()

    return {"message": "User registered"}


# --- POST /auth/login ---------------------------------------------
@router.post("/login")
def user_login(user: UserLogin, db: Session=Depends(get_db)):
    """
    User login that verifies that the input username/email and password are correct
    """
    user_id = db.scalar(select(User).where(or_(User.username == user.username, User.email == user.email)))
    if not user_id or not password_hash.verify(user.password, user_id.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Username/Email or Password", headers={"WWW-Authenticate": "Bearer"})
    
    payload = {
        "sub": str(user_id.id), 
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_LIFETIME_MINUTES)
        }
    
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    login_token = Token(access_token = encoded_jwt, token_type = "bearer")

    return login_token

# --- get_current_user dependency ------------------------------------
def get_current_user(token=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    user_id = int(payload["sub"])
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    return user
        
