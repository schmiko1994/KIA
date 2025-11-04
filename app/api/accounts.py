"""Account management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.account import Account, AccountStatus
from app.utils.logger import app_logger

router = APIRouter()


# Pydantic schemas
class AccountCreate(BaseModel):
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    proxy_id: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[str] = None


class AccountUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    proxy_id: Optional[int] = None
    status: Optional[AccountStatus] = None
    notes: Optional[str] = None
    tags: Optional[str] = None


class AccountResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    email: Optional[str]
    status: AccountStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account_data: AccountCreate, db: AsyncSession = Depends(get_db)):
    """Create a new TikTok account"""
    try:
        account = Account(**account_data.model_dump())
        db.add(account)
        await db.commit()
        await db.refresh(account)
        app_logger.info(f"Account created: {account.username}")
        return account
    except Exception as e:
        await db.rollback()
        app_logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[AccountStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all accounts"""
    try:
        query = select(Account)
        if status_filter:
            query = query.where(Account.status == status_filter)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        accounts = result.scalars().all()
        return accounts
    except Exception as e:
        app_logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Get account by ID"""
    try:
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update account"""
    try:
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        for key, value in account_data.model_dump(exclude_unset=True).items():
            setattr(account, key, value)
        
        await db.commit()
        await db.refresh(account)
        app_logger.info(f"Account updated: {account.username}")
        return account
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        app_logger.error(f"Error updating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Delete account"""
    try:
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        await db.delete(account)
        await db.commit()
        app_logger.info(f"Account deleted: {account.username}")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        app_logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/activate", response_model=AccountResponse)
async def activate_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Activate account"""
    try:
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        account.status = AccountStatus.ACTIVE
        await db.commit()
        await db.refresh(account)
        app_logger.info(f"Account activated: {account.username}")
        return account
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        app_logger.error(f"Error activating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/suspend", response_model=AccountResponse)
async def suspend_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Suspend account"""
    try:
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        account.status = AccountStatus.SUSPENDED
        await db.commit()
        await db.refresh(account)
        app_logger.info(f"Account suspended: {account.username}")
        return account
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        app_logger.error(f"Error suspending account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_account_stats(db: AsyncSession = Depends(get_db)):
    """Get account statistics overview"""
    try:
        total = await db.scalar(select(func.count()).select_from(Account))
        active = await db.scalar(select(func.count()).select_from(Account).where(Account.status == AccountStatus.ACTIVE))
        suspended = await db.scalar(select(func.count()).select_from(Account).where(Account.status == AccountStatus.SUSPENDED))
        
        return {
            "total": total or 0,
            "active": active or 0,
            "suspended": suspended or 0,
            "banned": 0
        }
    except Exception as e:
        app_logger.error(f"Error getting account stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
