from fastapi import APIRouter
from models import PublicInfoResponse

router = APIRouter(tags=["Public"])

@router.get(
    "/public/info",
    response_model=PublicInfoResponse,
    summary="Read public open data",
    description="An open endpoint that anyone can access without authentication."
)
async def get_public_info():
    return {
        "message": "Welcome stranger! This info is public.",
        "version": "1.0.0",
        "identity_provider": "Supabase Auth"
    }
