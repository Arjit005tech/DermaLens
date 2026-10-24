from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from database import Base


# ---------- SQLAlchemy ORM models (database tables) ----------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    reports = relationship("Report", back_populates="owner")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    predicted_class = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    original_image_path = Column(String, nullable=False)
    heatmap_image_path = Column(String, nullable=False)
    recommendation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="reports")


# ---------- Pydantic schemas (API request/response shapes) ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ReportOut(BaseModel):
    id: int
    predicted_class: str
    confidence: float
    original_image_path: str
    heatmap_image_path: str
    recommendation: str | None
    created_at: datetime

    class Config:
        from_attributes = True
