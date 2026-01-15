from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
import json
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="regular")  # "admin" or "regular"

    # Relationship
    animals = relationship("Animal", back_populates="responsible_user")


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    _form_ids = Column("form_ids", Text, default="[]")  # JSON string for SQLite compatibility
    responsible_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Son form durumları (son formdan kopyalanacak)
    is_controlled = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    need_review = Column(Boolean, default=False)
    last_form_sent_date = Column(DateTime, nullable=True)
    
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


class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id", ondelete="CASCADE"), nullable=False)
    
    # Form durumu
    is_sent = Column(Boolean, default=False)
    is_controlled = Column(Boolean, default=False)
    need_review = Column(Boolean, default=False)
    
    # Tarihler
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    send_date = Column(DateTime, nullable=True)
    control_due_date = Column(DateTime, nullable=True)  # send_date + 1 hafta
    controlled_date = Column(DateTime, nullable=True)

    # Relationship
    animal = relationship("Animal", back_populates="forms")
