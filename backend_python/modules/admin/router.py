from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from config import config

router = APIRouter(prefix="/admin", tags=["admin"])


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(req: LoginRequest):
    if req.password != config.ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if not config.APP_SECRET_TOKEN:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="APP_SECRET_TOKEN not configured")
    return {"token": config.APP_SECRET_TOKEN}
