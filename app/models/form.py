"""Form model"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime


class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id", ondelete="CASCADE"), nullable=False)
    
    # Form durumu - Yeni akış
    # Status: created, sent, filled, controlled
    form_status = Column(String, default="created", nullable=False)
    
    # Tarihler
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_date = Column(DateTime, nullable=True)  # Görev atama tarihi (is_sent olduğunda)
    filled_date = Column(DateTime, nullable=True)  # Doldurma/dönüş tarihi (is_filled olduğunda)
    controlled_date = Column(DateTime, nullable=True)  # İnceleme tarihi (is_controlled olduğunda)
    control_due_date = Column(DateTime, nullable=True)  # İnceleme son tarih

    # Relationship
    animal = relationship("Animal", back_populates="forms")
