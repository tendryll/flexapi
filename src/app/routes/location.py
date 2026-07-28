"""/location endpoints — thin HTTP layer delegating to the service."""

from fastapi import APIRouter, HTTPException, status

from ..model.models import CoordinateResponse
from ..service import service

router = APIRouter(prefix="/location", tags=["location"])

@router.get(path="/location", status_code=status.HTTP_200_OK)
async def get_coordinates() -> list[CoordinateResponse]:
    try:
        return await service.get_coordinates()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
