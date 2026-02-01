from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import httpx
from typing import List

from common.database import get_async_db
from common import models, schemas
from common.config import settings
from app.api import deps

router = APIRouter()

@router.get("", response_model=List[schemas.UserIntegration])
async def list_integrations(
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    stmt = select(models.UserIntegration).where(models.UserIntegration.user_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/github/auth-url")
async def get_github_auth_url(current_user: models.User = Depends(deps.get_current_user)):
    """Returns GitHub OAuth URL for frontend to redirect."""
    scope = "repo,read:user"
    url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope={scope}&state={current_user.id}"
    return {"url": url}

@router.get("/github/login")
async def github_login(
    user_id: int = None,
    current_user: models.User = Depends(deps.get_current_user_optional)
):
    """Redirects to GitHub for OAuth. Supports both authenticated and query param modes."""
    # Use user_id from query param if provided, otherwise from current_user
    uid = user_id if user_id else (current_user.id if current_user else None)
    if not uid:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    scope = "repo,read:user"
    url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope={scope}&state={uid}"
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(
    code: str, 
    state: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Handles GitHub OAuth callback."""
    # State is user_id
    user_id = int(state)
    
    async with httpx.AsyncClient() as client:
        # 1. Exchange code for token
        res = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI
            },
            headers={"Accept": "application/json"}
        )
        res_data = res.json()
        access_token = res_data.get("access_token")
        
        if not access_token:
             raise HTTPException(status_code=400, detail=f"Failed to get GitHub token: {res_data}")
        
        # 2. Get GitHub User ID (optional but good for uniqueness)
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        github_user = user_res.json()
        github_id = str(github_user.get("id"))
        
        # 3. Save or Update Integration
        stmt = select(models.UserIntegration).where(
            models.UserIntegration.user_id == user_id,
            models.UserIntegration.provider == "github"
        )
        result = await db.execute(stmt)
        integration = result.scalar_one_or_none()
        
        if integration:
            integration.access_token = access_token
            integration.provider_user_id = github_id
        else:
            integration = models.UserIntegration(
                user_id=user_id,
                provider="github",
                access_token=access_token,
                provider_user_id=github_id
            )
            db.add(integration)
            
        await db.commit()
        
    # Redirect back to frontend
    # Assuming frontend URL from settings or just /my/portfolios/new
    frontend_url = f"{settings.BACKEND_URL.replace('api.', '').replace(':8000', ':3000')}/my/portfolios/new?connected=github"
    # Actually, we should probably redirect to a specific success page or just back with a param.
    return RedirectResponse(frontend_url)

@router.get("/github/repos")
async def list_github_repos(
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Lists repositories (public & private) for the connected GitHub account."""
    stmt = select(models.UserIntegration).where(
        models.UserIntegration.user_id == current_user.id,
        models.UserIntegration.provider == "github"
    )
    result = await db.execute(stmt)
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=400, detail="GitHub not connected")
    
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"token {integration.access_token}"},
            params={"sort": "pushed", "per_page": 100}
        )
        if res.status_code != 200:
             raise HTTPException(status_code=res.status_code, detail="Failed to fetch repos from GitHub")
        
        repos = res.json()
        # Simplify data for frontend
        return [{
            "name": r["full_name"],
            "url": r["html_url"],
            "private": r["private"],
            "description": r["description"]
        } for r in repos]

@router.delete("/{integration_id}")
async def remove_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    stmt = delete(models.UserIntegration).where(
        models.UserIntegration.id == integration_id,
        models.UserIntegration.user_id == current_user.id
    )
    await db.execute(stmt)
    await db.commit()
    return {"success": True}
