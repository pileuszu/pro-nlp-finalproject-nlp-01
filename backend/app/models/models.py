from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, JSON, Table, Enum as SqEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

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
    location = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cover_letters = relationship("CoverLetter", back_populates="recruitment")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False) # Original File Name or Main Title
    type = Column(String, nullable=False)  # github, link, file, notion
    source_url = Column(String, nullable=True)
    content = Column(Text, nullable=True) # Raw extracted text
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # LLM Extracted Metadata (User Profile)
    processing_status = Column(SqEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    extracted_summary = Column(Text, nullable=True)
    extracted_job_title = Column(String, nullable=True)
    
    # Project Details (Flattened)
    project_name = Column(String, nullable=True)
    period = Column(String, nullable=True)
    role = Column(String, nullable=True)
    description = Column(Text, nullable=True) # Refined Description for Embedding
    tech_stack = Column(JSON, nullable=True) # List of strings

    owner = relationship("User", back_populates="portfolios")
    job_queries = relationship("PortfolioJobQuery", back_populates="portfolio", cascade="all, delete-orphan")

class PortfolioJobQuery(Base):
    __tablename__ = "portfolio_job_queries"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    type = Column(String, nullable=True) # A, B, C
    query_text = Column(String, nullable=True)
    evidence = Column(JSON, nullable=True) # List of strings

    portfolio = relationship("Portfolio", back_populates="job_queries")

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
