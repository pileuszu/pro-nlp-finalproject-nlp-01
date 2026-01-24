from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    profile_image: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Recruitment Schemas
class RecruitmentBase(BaseModel):
    title: str
    company: str
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None

class RecruitmentCreate(RecruitmentBase):
    pass

class Recruitment(RecruitmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Portfolio Schemas
class PortfolioBase(BaseModel):
    title: str
    type: str
    source_url: Optional[str] = None
    content: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    user_id: int

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Cover Letter Schemas
class CoverLetterBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    recruit_id: int

class CoverLetterCreate(CoverLetterBase):
    user_id: int

class CoverLetter(CoverLetterBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# AI Related Schemas
class PortfolioAnalyzeRequest(BaseModel):
    source: str
    type: str  # github, link, file, notion

class CoverLetterGenerateRequest(BaseModel):
    recruitId: int
    portfolioIds: List[int]
    question: str
    tone: str = "professional"
