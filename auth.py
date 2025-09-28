# auth.py
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db import SessionLocal
from models import User

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'cambia_esto')
JWT_EXP_MINUTES = int(os.getenv('JWT_EXP_MINUTES', '120'))

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def create_token(user_id: int, role: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': int(exp.timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except Exception:
        return None

def get_user_from_token(token: str):
    payload = verify_token(token)
    if not payload:
        return None
    db = SessionLocal()
    user = db.query(User).filter(User.id == int(payload.get('user_id'))).first()
    db.close()
    return user
