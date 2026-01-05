"""Cities API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models import City
from app.schemas import CityResponse

router = APIRouter(prefix="/cities", tags=["Cities"])

# Hardcoded metropolitan cities for Phase 1
METRO_CITIES = [
    {"id": 1, "name": "Mumbai", "code": "MUM", "state": "Maharashtra"},
    {"id": 2, "name": "Delhi NCR", "code": "DEL", "state": "Delhi"},
    {"id": 3, "name": "Bangalore", "code": "BLR", "state": "Karnataka"},
    {"id": 4, "name": "Hyderabad", "code": "HYD", "state": "Telangana"},
    {"id": 5, "name": "Chennai", "code": "CHE", "state": "Tamil Nadu"},
    {"id": 6, "name": "Kolkata", "code": "KOL", "state": "West Bengal"},
    {"id": 7, "name": "Pune", "code": "PUN", "state": "Maharashtra"},
    {"id": 8, "name": "Ahmedabad", "code": "AHM", "state": "Gujarat"},
]


@router.get("", response_model=list[CityResponse])
async def get_cities(
    db: AsyncSession = Depends(get_db),
) -> list[CityResponse]:
    """
    Get list of supported metropolitan cities.
    
    Returns all cities where movie booking stats are available.
    """
    # Try to get from database first
    result = await db.execute(select(City).where(City.is_active == True))
    cities = result.scalars().all()
    
    if cities:
        return [CityResponse.model_validate(city) for city in cities]
    
    # Fallback to hardcoded list
    return [CityResponse(**city) for city in METRO_CITIES]


@router.get("/{city_code}", response_model=CityResponse)
async def get_city(
    city_code: str,
    db: AsyncSession = Depends(get_db),
) -> CityResponse:
    """Get city details by code."""
    result = await db.execute(
        select(City).where(City.code == city_code.upper())
    )
    city = result.scalar_one_or_none()
    
    if city:
        return CityResponse.model_validate(city)
    
    # Fallback to hardcoded
    for c in METRO_CITIES:
        if c["code"] == city_code.upper():
            return CityResponse(**c)
    
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"City {city_code} not found")
