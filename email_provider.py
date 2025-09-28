# email_provider.py
import os
import requests
from dotenv import load_dotenv
from time import sleep

load_dotenv()
EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'console')
EMAIL_API_KEY = os.getenv('EMAIL_API_KEY', '')
EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'noreply@example.com')

def send_verification_email(email: str, username: str, code: str) -> bool:
    """
    Envía un email de verificación. Por defecto imprime en consola.
    Se soporta 'mailjet' mediante API Key en formato key:secret.
    """
    if EMAIL_PROVIDER == 'console' or not EMAIL_API_KEY:
        print(f"[SIMULADO] Enviar a {email}: Hola {username}, tu código es {code}")
        return True

    if EMAIL_PROVIDER == 'mailjet':
        try:
            api_key, api_secret = EMAIL_API_KEY.split(':',1)
            url = 'https://api.mailjet.com/v3.1/send'
            data = {
                'Messages': [
                    {
                        'From': {'Email': EMAIL_SENDER, 'Name': 'MiControlKit'},
                        'To': [{'Email': email, 'Name': username}],
                        'Subject': 'Verificación de cuenta',
                        'HTMLPart': f'<p>Hola {username},</p><p>Tu código de verificación es <b>{code}</b></p>'
                    }
                ]
            }
            for attempt in range(3):
                r = requests.post(url, json=data, auth=(api_key, api_secret), timeout=10)
                if r.status_code == 200:
                    return True
                sleep(1)
            return False
        except Exception as e:
            print('Error enviando Mailjet:', e)
            return False

    # Otros proveedores pueden añadirse aquí
    print('Proveedor no soportado o API key faltante')
    return False
