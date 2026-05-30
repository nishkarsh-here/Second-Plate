"""Surplus listing endpoints: create, browse, detail, claim, and per-donor."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user_optional
from app.core.errors import BadRequestError
from app.db.session import get_db
from app.models.enums import FoodCategory, ListingStatus, UserRole
from app.models.user import User
from app.schemas.listing import ListingCreate, ListingDetail, ListingOut
from app.schemas.pickup import ClaimRequest, PickupOut
from app.services import listings_service

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post(
    "",
    response_model=ListingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a surplus food listing (donor)",
)
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> ListingOut:
    # Authenticated donors post as themselves; guests pass a donor_id.
    if user is not None and user.role == UserRole.donor and user.donor_id:
        payload.donor_id = user.donor_id
    if payload.donor_id is None:
        raise BadRequestError("Sign in as a donor, or provide a donor_id.")
    return listings_service.create_listing(db, payload)


@router.get(
    "",
    response_model=list[ListingOut],
    summary="Browse listings, sorted by urgency then distance",
)
def browse_listings(
    db: Session = Depends(get_db),
    lat: float | None = Query(None, ge=-90, le=90, description="Viewer latitude"),
    lng: float | None = Query(None, ge=-180, le=180, description="Viewer longitude"),
    radius: float | None = Query(None, gt=0, description="Filter radius in km (needs lat/lng)"),
    listing_status: ListingStatus | None = Query(
        ListingStatus.available, alias="status", description="Filter by status"
    ),
    category: FoodCategory | None = Query(None, description="Filter by food category"),
    limit: int = Query(100, ge=1, le=500),
) -> list[ListingOut]:
    return listings_service.list_listings(
        db, lat=lat, lng=lng, radius_km=radius, status=listing_status, category=category, limit=limit
    )


@router.get(
    "/donor/{donor_id}",
    response_model=list[ListingOut],
    summary="A donor's own listings (My Listings)",
)
def donor_listings(
    donor_id: int = Path(..., ge=1), db: Session = Depends(get_db)
) -> list[ListingOut]:
    return listings_service.list_donor_listings(db, donor_id)


@router.get("/{listing_id}", response_model=ListingDetail, summary="Listing detail")
def listing_detail(
    listing_id: int = Path(..., ge=1), db: Session = Depends(get_db)
) -> ListingDetail:
    return listings_service.get_listing(db, listing_id)


@router.post(
    "/{listing_id}/claim",
    response_model=PickupOut,
    status_code=status.HTTP_201_CREATED,
    summary="Claim a listing for pickup (recipient)",
)
def claim_listing(
    payload: ClaimRequest,
    listing_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> PickupOut:
    # Authenticated recipients claim as themselves; guests pass a recipient_id.
    if user is not None and user.role == UserRole.recipient and user.recipient_id:
        payload.recipient_id = user.recipient_id
    if payload.recipient_id is None:
        raise BadRequestError("Sign in as a recipient, or provide a recipient_id.")
    return listings_service.claim_listing(db, listing_id, payload)
