# MiControlKit — Kit para proteger y administrar tu app (Cerebrito)

Este repositorio contiene una versión protegida de tu aplicación `CEREBRITO_WEB_2025_v4.py` (ahora `target_app.py`)
y un panel de administración para crear usuarios, verificar por email y asignar créditos.

## Archivos principales

- `target_app.py` — versión protegida del analizador; verifica token y créditos antes de ejecutar.
- `adminpanel.py` — panel de administración (Streamlit) para admins.
- `login.py` — script de consola para usuarios que quieran guardar un token local.
- `create_db.py` — inicializa la base de datos y crea un superadmin.
- `models.py`, `db.py`, `auth.py`, `utils.py`, `email_provider.py` — utilidades y módulos.
- `requirements.txt`, `.env.example`, `README.md`.

## Instalación (pasos para principiantes)

1. Clona o descarga la carpeta y sitúala en tu máquina local.
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # linux / mac
   venv\Scripts\activate    # windows
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copia `.env.example` a `.env` y edita las variables necesarias (al menos: `SECRET_KEY`, `SUPERADMIN_PASSWORD` si deseas).
5. Inicializa la base de datos y crea superadmin:
   ```bash
   python create_db.py
   ```
   Aparecerán las credenciales del superadmin (por defecto las definidas en `.env`).

6. Ejecuta el panel de administración (para crear usuarios y asignar créditos):
   ```bash
   streamlit run adminpanel.py
   ```

7. Para que un usuario normal pueda ejecutar la app protegida:
   - Debe estar verificado y tener créditos.
   - Puede ejecutar `python login.py` para guardar un token local (archivo en tu home `.mi_control_kit_session.json`).
   - Luego ejecutar:
     ```bash
     streamlit run target_app.py
     ```
   - Si no tiene token o créditos, la app mostrará instrucciones y no permitirá la ejecución.

## Notas de seguridad y limitaciones

- **No es posible evitar que alguien lea el código** si tiene acceso al sistema de ficheros. Lo que este kit hace es que la app **no funcione** sin autenticación y créditos.
- Para ofuscar el código, puedes empaquetar `target_app.py` con PyInstaller, pero no es 100% seguro.
- No guardes claves en el repositorio en texto plano. Usa `.env` y `.gitignore`.

## Proveedores de email

Por defecto el envío de correo está en modo `console` (simulado). Para producción configura:
- `EMAIL_PROVIDER=mailjet` y `EMAIL_API_KEY=APIKEY:APISECRET`

También puedes adaptar `email_provider.py` para SendGrid, Mailgun, etc.

## Despliegue en share.streamlit.io

- Sube el repo a GitHub.
- Asegúrate de que `requirements.txt` esté presente.
- Streamlit Cloud no permite acceder a variables de `.env` en repos privado sin configuración; para pruebas públicas puedes usar env vars en el panel de Streamlit Cloud.
- Ten en cuenta: compartir `target_app.py` en Streamlit presupondrá que los usuarios puedan iniciar sesión; para demo considera usar `EMAIL_PROVIDER=console` y precrear usuarios con créditos.

## Tests

Hay tests básicos propuestos en `tests/` (no incluidos en esta primera entrega). Usa `pytest` para ejecutarlos.

## Cómo proceder

Si quieres, puedo:
- Compactar todos los archivos en un zip y dejarlo listo para descargar.
- Añadir tests pytest básicos.
- Integrar un flujo de verificación por link (además del código).
