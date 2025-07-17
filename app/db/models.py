from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

class ApiRequest(Base):
    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    operation_type = Column(String, index=True)
    input_params = Column(String)
    result = Column(Float)
    client_ip = Column(String, nullable=True) # Poate fi null daca nu il putem obtine