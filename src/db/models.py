"""SQLAlchemy database models."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AlertHistory(Base):
    """Record of processed emails and their classifications."""
    
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String(255), unique=True, index=True)
    sender = Column(String(255))
    subject = Column(String(500))
    snippet = Column(Text)
    urgency = Column(String(20))  # URGENT or NOT_URGENT
    reason = Column(Text)
    sms_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AlertHistory {self.email_id}: {self.urgency}>"


class VIPSender(Base):
    """VIP sender that automatically triggers URGENT classification."""
    
    __tablename__ = "vip_senders"
    
    id = Column(Integer, primary_key=True, index=True)
    email_or_domain = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VIPSender {self.email_or_domain}>"


class KeywordRule(Base):
    """Keyword that triggers URGENT classification when found in email."""
    
    __tablename__ = "keyword_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<KeywordRule {self.keyword}>"


class Settings(Base):
    """System settings stored as key-value pairs."""
    
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Settings {self.key}={self.value}>"
