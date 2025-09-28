# models.py
# Definición de tablas usando SQLAlchemy (User y AuditLog)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='user')
    verified = Column(Boolean, default=False)
    credits = Column(Integer, default=0)
    unlimited = Column(Boolean, default=False)
    verification_code = Column(String(10), nullable=True)
    verification_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class AuditLog(Base):
    __tablename__ = 'auditlog'
    id = Column(Integer, primary_key=True)
    actor = Column(String(150))
    action = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())
