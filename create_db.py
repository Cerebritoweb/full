# create_db.py
# Inicializa la DB y crea un superadmin con credenciales definidas en .env
import os
from db import init_db, SessionLocal
from models import User, AuditLog
from auth import hash_password
from dotenv import load_dotenv

load_dotenv()
SUPERADMIN_USERNAME = os.getenv('SUPERADMIN_USERNAME', 'superadmin')
SUPERADMIN_PASSWORD = os.getenv('SUPERADMIN_PASSWORD', 'cambiar_en_el_primer_login')

def main():
    init_db()
    db = SessionLocal()
    existing = db.query(User).filter(User.username == SUPERADMIN_USERNAME).first()
    if existing:
        print('Superadmin ya existe. Si quieres recrearlo borra la DB y vuelve a ejecutar.')
        return

    sa = User(
        username=SUPERADMIN_USERNAME,
        email='superadmin@local',
        password_hash=hash_password(SUPERADMIN_PASSWORD),
        role='superadmin',
        verified=True,
        credits=0,
        unlimited=True
    )
    db.add(sa)
    db.add(AuditLog(actor='system', action=f'Creado superadmin {SUPERADMIN_USERNAME}'))
    db.commit()
    db.close()
    print('Base de datos inicializada. Superadmin creado:')
    print('  usuario:', SUPERADMIN_USERNAME)
    print('  contraseña:', SUPERADMIN_PASSWORD)
    print('CAMBIA la contraseña del superadmin en el primer login.')

if __name__ == '__main__':
    main()
