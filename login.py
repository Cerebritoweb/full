# login.py
# Script de consola para que un usuario inicie sesión y guarde un token local en .session_token
import os
import json
from db import SessionLocal
from auth import verify_password, create_token
from models import User
from pathlib import Path

SESSION_PATH = Path.home() / '.mi_control_kit_session.json'

def save_token(token):
    SESSION_PATH.write_text(json.dumps({'token': token}), encoding='utf-8')
    print('Token guardado en', SESSION_PATH)

def main():
    username = input('Usuario: ').strip()
    password = input('Contraseña: ').strip()
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print('Usuario no existe')
        return
    if not user.verified:
        print('Usuario no verificado. Verifica tu cuenta primero.')
        return
    if not verify_password(password, user.password_hash):
        print('Credenciales inválidas')
        return
    token = create_token(user.id, user.role)
    save_token(token)
    print('Login OK. Ahora puedes ejecutar target_app.py si tienes créditos.')

if __name__ == '__main__':
    main()
