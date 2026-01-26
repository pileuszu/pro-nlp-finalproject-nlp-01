from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    profile_image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    portfolios = relationship("Portfolio", back_populates="owner")
    cover_letters = relationship("CoverLetter", back_populates="owner")

class Recruitment(Base):
    __tablename__ = "recruitments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    start_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    content = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List of strings
    category = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cover_letters = relationship("CoverLetter", back_populates="recruitment")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # github, link, file, notion
    source_url = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="portfolios")

class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recruitment_id = Column(Integer, ForeignKey("recruitments.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="cover_letters")
    recruitment = relationship("Recruitment", back_populates="cover_letters")
