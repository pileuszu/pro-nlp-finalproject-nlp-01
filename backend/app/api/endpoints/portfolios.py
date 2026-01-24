from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas import schemas
from app.services import portfolio_service

router = APIRouter()

@router.get("/", response_model=dict)
async def list_portfolios(db: Session = Depends(get_db)):
    # In a real app, user_id would come from the auth token
    user_id = 1 
    items = portfolio_service.get_portfolios(db, user_id=user_id)
    return {"items": items}

@router.post("/", response_model=schemas.Portfolio, status_code=201)
async def create_portfolio(portfolio: schemas.PortfolioCreate, db: Session = Depends(get_db)):
    return portfolio_service.create_portfolio(db, portfolio)

@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    user_id = 1
    success = portfolio_service.delete_portfolio(db, portfolio_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio not found or unauthorized")
    return {"success": True, "message": "Portfolio deleted"}

@router.post("/analyze", response_model=List[dict])
async def analyze_portfolio(req: schemas.PortfolioAnalyzeRequest):
    """Mocks AI analysis of a portfolio source."""
    return portfolio_service.mock_analyze_portfolio(req.source, req.type)
