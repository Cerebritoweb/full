# adminpanel.py
# Streamlit admin panel para crear usuarios, dar créditos, verificar y ver logs.
import streamlit as st
from db import SessionLocal, init_db
from models import User, AuditLog
from auth import verify_password, create_token, hash_password
from email_provider import send_verification_email
from utils import generate_code, expires_in_minutes
from dotenv import load_dotenv
import os
from auth import get_user_from_token

load_dotenv()
CREDIT_COST_PER_RUN = int(os.getenv('CREDIT_COST_PER_RUN', '1'))
VERIFICATION_CODE_EXP_MIN = int(os.getenv('VERIFICATION_CODE_EXP_MIN', '10'))

init_db()
st.set_page_config(page_title='Admin Panel - MiControlKit')

if 'admin' not in st.session_state:
    st.session_state['admin'] = None

def log_action(actor, action):
    db = SessionLocal()
    db.add(AuditLog(actor=actor, action=action))
    db.commit()
    db.close()

def try_login(username, password):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password_hash) and user.verified and user.role in ('superadmin','admin'):
        token = create_token(user.id, user.role)
        st.session_state['admin'] = {'id': user.id, 'username': user.username, 'role': user.role, 'token': token}
        log_action(user.username, 'login_admin')
        db.close()
        return True
    db.close()
    return False

st.title('MiControlKit — Panel de Administración')

if not st.session_state['admin']:
    st.subheader('Login (admin)')
    with st.form('login'):
        username = st.text_input('Usuario')
        password = st.text_input('Contraseña', type='password')
        submitted = st.form_submit_button('Entrar')
        if submitted:
            ok = try_login(username, password)
            if not ok:
                st.error('Credenciales inválidas, usuario no verificado o sin permisos')
            else:
                st.success('Login exitoso')
                st.experimental_rerun()
else:
    admin = st.session_state['admin']
    st.sidebar.write(f"Conectado como: {admin['username']} ({admin['role']})")
    if st.sidebar.button('Cerrar sesión'):
        st.session_state['admin'] = None
        st.experimental_rerun()

    tab = st.sidebar.radio('Sección', ['Usuarios','Créditos','Verificación','Logs','Ajustes'])

    db = SessionLocal()

    if tab == 'Usuarios':
        st.header('Usuarios')
        q = st.text_input('Buscar usuario (username o email)')
        if q:
            users = db.query(User).filter((User.username.contains(q)) | (User.email.contains(q))).all()
        else:
            users = db.query(User).all()
        for u in users:
            st.write(f"- {u.username} | {u.email} | rol: {u.role} | verif: {u.verified} | credits: {u.credits} | unlimited: {u.unlimited}")
            cols = st.columns([1,1,1,1])
            if cols[0].button('Borrar', key=f'del_{u.id}'):
                if u.role == 'superadmin':
                    st.warning('No puedes borrar superadmin desde la UI')
                else:
                    db.delete(u)
                    db.commit()
                    log_action(admin['username'], f'borrar usuario {u.username}')
                    st.experimental_rerun()
            if cols[1].button('Reset pass', key=f'reset_{u.id}'):
                u.password_hash = hash_password(u.username + '123')
                db.commit()
                log_action(admin['username'], f'reset password {u.username}')
                st.success('Contraseña reseteada (temporal). Indica al usuario que la cambie.')
            if cols[2].button('Verificar', key=f'ver_{u.id}'):
                u.verified = True
                db.commit()
                log_action(admin['username'], f'verificar {u.username}')
                st.experimental_rerun()
            if cols[3].button('Editar', key=f'edit_{u.id}'):
                st.info('Editar en línea')
                new_email = st.text_input('Nuevo email', value=u.email, key=f'email_{u.id}')
                if st.button('Guardar', key=f'guardar_{u.id}'):
                    u.email = new_email
                    db.commit()
                    log_action(admin['username'], f'editar {u.username}')
                    st.experimental_rerun()

        st.subheader('Crear nuevo usuario')
        with st.form('create_user'):
            new_user = st.text_input('Usuario')
            new_email = st.text_input('Email')
            new_pass = st.text_input('Contraseña', type='password')
            created = st.form_submit_button('Crear')
            if created:
                exists = db.query(User).filter((User.username == new_user) | (User.email == new_email)).first()
                if exists:
                    st.error('Usuario o email ya existe')
                else:
                    user = User(username=new_user, email=new_email, password_hash=hash_password(new_pass), role='user', verified=False, credits=0)
                    db.add(user)
                    db.commit()
                    log_action(admin['username'], f'crear usuario {new_user}')
                    code = generate_code(6)
                    user.verification_code = code
                    user.verification_expires_at = expires_in_minutes(VERIFICATION_CODE_EXP_MIN)
                    db.commit()
                    send_verification_email(new_email, new_user, code)
                    st.success('Usuario creado. Se envió código de verificación.')
                    st.experimental_rerun()

    if tab == 'Créditos':
        st.header('Gestionar créditos')
        users = db.query(User).all()
        sel = st.selectbox('Selecciona usuario', [f"{u.id} | {u.username}" for u in users])
        if sel:
            uid = int(sel.split('|')[0].strip())
            u = db.query(User).filter(User.id == uid).first()
            st.write(f"Usuario: {u.username} | créditos: {u.credits} | ilimitado: {u.unlimited}")
            add = st.number_input('Agregar créditos', min_value=0, value=0)
            sub = st.number_input('Quitar créditos', min_value=0, value=0)
            unlimited = st.checkbox('Marcar ilimitado', value=u.unlimited)
            if st.button('Aplicar cambios'):
                if add > 0:
                    u.credits += int(add)
                if sub > 0:
                    u.credits = max(0, u.credits - int(sub))
                u.unlimited = unlimited
                db.commit()
                log_action(admin['username'], f'cambiar creditos {u.username} +{add} -{sub} unlimited={unlimited}')
                st.success('Cambios aplicados')
                st.experimental_rerun()

    if tab == 'Verificación':
        st.header('Verificaciones pendientes')
        pend = db.query(User).filter(User.verified == False).all()
        for p in pend:
            st.write(f"- {p.username} | {p.email} | code: {p.verification_code}")
            if st.button('Reenviar', key=f'reenv_{p.id}'):
                code = generate_code(6)
                p.verification_code = code
                p.verification_expires_at = expires_in_minutes(VERIFICATION_CODE_EXP_MIN)
                db.commit()
                send_verification_email(p.email, p.username, code)
                log_action(admin['username'], f'reenviar verif {p.username}')
                st.success('Código reenviado')

    if tab == 'Logs':
        st.header('Audit Log')
        logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(200).all()
        for l in logs:
            st.write(f"{l.timestamp} | {l.actor} | {l.action}")

    if tab == 'Ajustes':
        st.header('Ajustes (solo superadmin puede cambiar valores sensibles)')
        if admin['role'] != 'superadmin':
            st.info('Solo superadmin puede modificar ajustes sensibles')
        else:
            st.write('CREDIT_COST_PER_RUN actual: ' + str(os.getenv('CREDIT_COST_PER_RUN', '1')))
            new_cost = st.number_input('Nuevo costo por ejecución (creditos)', min_value=0, value=int(os.getenv('CREDIT_COST_PER_RUN', '1')))
            if st.button('Aplicar costo'):
                # Para conservar simple, instruct user to edit .env in deployment
                st.warning('Por seguridad se requiere editar .env en el servidor para cambiar este valor. - Acciones sensibles fuera de la UI.')
