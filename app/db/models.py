from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime
import uuid

class ApiRequest(Base):
    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    operation_type = Column(String, index=True)
    input_params = Column(String)
    result = Column(String)
    client_ip = Column(String, nullable=True) # Poate fi null daca nu il putem obtine

class ApiKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)