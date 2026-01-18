"""Animal model"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
import json


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    _form_ids = Column("form_ids", Text, default="[]")  # JSON string for SQLite compatibility
    responsible_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Son form durumu (son formdan kopyalanacak)
    # Status: created, sent, filled, controlled
    form_status = Column(String, default="created", nullable=False)
    last_form_sent_date = Column(DateTime, nullable=True)
    last_form_created_date = Column(DateTime, nullable=True)
    
    owner_name = Column(String, nullable=False)
    owner_contact_number = Column(String, nullable=False)
    owner_contact_email = Column(String, nullable=False)
    form_generation_period = Column(Integer, nullable=False)  # Months between form generation

    # Property to handle form_ids as list
    @property
    def form_ids(self):
        if self._form_ids:
            return json.loads(self._form_ids)
        return []
    
    @form_ids.setter
    def form_ids(self, value):
        self._form_ids = json.dumps(value)

    # Relationships
    responsible_user = relationship("User", back_populates="animals")
    forms = relationship("Form", back_populates="animal", cascade="all, delete-orphan", order_by="Form.id.desc()")
