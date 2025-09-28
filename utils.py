# utils.py
from datetime import datetime, timedelta
import random

def generate_code(n=6):
    return ''.join(str(random.randint(0,9)) for _ in range(n))

def expires_in_minutes(minutes):
    return datetime.utcnow() + timedelta(minutes=minutes)
