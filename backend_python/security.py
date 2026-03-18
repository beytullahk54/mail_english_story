from fastapi import Header, HTTPException, status
from config import config


def verify_token(x_api_token: str = Header(..., description="API güvenlik token'ı")):
    """
    İstekte 'X-Api-Token' header'ı zorunludur.
    Değer config.API_TOKEN ile eşleşmezse 401 döner.
    """
    if not config.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sunucuda API_TOKEN tanımlı değil.",
        )
    if x_api_token != config.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya eksik token.",
        )
