from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class PhaseRecord(Base):
    __tablename__ = "phase_records"

    id = Column(Integer, primary_key=True, index=True)
    pilot_name = Column(String, nullable=False, index=True)
    last_phase = Column(Integer, nullable=False)
    device_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
