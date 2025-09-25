from fastapi import APIRouter, Depends, HTTPException, Header, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/auth", tags=["authentication"])

def get_current_user(api_key: str = Header(..., alias="api-key"), db: Session = Depends(get_db)):
    """Get current user from API key"""
    user = db.query(models.User).filter(models.User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

def require_role(required_role: str):
    """Role-based access control decorator"""
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions. Required: {required_role}, has: {current_user.role}"
            )
        return current_user
    return role_checker

# Option 1: Using query parameters (simpler)
@router.post("/login")
def login(username: str, db: Session = Depends(get_db)):
    """Login and get API key"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"username": user.username, "api_key": user.api_key, "role": user.role}

# Option 2: Using request body (more RESTful)
@router.post("/login-json")
def login_json(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login using JSON request body"""
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"username": user.username, "api_key": user.api_key, "role": user.role}

# Get current user info
@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user information"""
    return current_user