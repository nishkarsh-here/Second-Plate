"""Business logic for surplus listings: create, browse (urgency/distance sort),
detail, and claim. Routers call into here and never touch the ORM directly.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.core.errors import ConflictError, NotFoundError
from app.core.time import as_utc, utcnow
from app.models import Donor, FoodListing, ListingStatus, Pickup, Recipient
from app.models.enums import FoodCategory
from app.schemas.donor import DonorBrief
from app.schemas.listing import ListingCreate, ListingOut
from app.schemas.pickup import ClaimRequest, PickupOut
from app.schemas.recipient import RecipientBrief
from app.services.geo import haversine_km
from app.services.urgency import compute_urgency


def serialize_listing(
    listing: FoodListing,
    now: datetime | None = None,
    origin: tuple[float, float] | None = None,
) -> ListingOut:
    """Build the API representation, attaching urgency and (optional) distance."""
    now = now or utcnow()
    urgency = compute_urgency(listing.category, listing.servings, listing.expires_at, now)
    distance_km = None
    if origin is not None:
        distance_km = round(haversine_km(origin[0], origin[1], listing.lat, listing.lng), 2)
    return ListingOut(
        id=listing.id,
        food_type=listing.food_type,
        category=listing.category,
        servings=listing.servings,
        prepared_at=listing.prepared_at,
        expires_at=listing.expires_at,
        status=listing.status,
        lat=listing.lat,
        lng=listing.lng,
        created_at=listing.created_at,
        donor=DonorBrief.model_validate(listing.donor),
        urgency=urgency,
        distance_km=distance_km,
    )


def expire_stale(db: Session) -> int:
    """Flip any still-'available' listings whose window has passed to 'expired'.

    Keeps the browse feed and impact numbers honest without a background job.
    """
    result = db.execute(
        update(FoodListing)
        .where(
            FoodListing.status == ListingStatus.available,
            FoodListing.expires_at < utcnow(),
        )
        .values(status=ListingStatus.expired)
    )
    db.commit()
    return result.rowcount or 0


def create_listing(db: Session, payload: ListingCreate) -> ListingOut:
    donor = db.get(Donor, payload.donor_id)
    if donor is None:
        raise NotFoundError(f"Donor {payload.donor_id} not found")

    listing = FoodListing(
        donor_id=donor.id,
        food_type=payload.food_type,
        category=payload.category,
        servings=payload.servings,
        prepared_at=as_utc(payload.prepared_at),
        expires_at=as_utc(payload.expires_at),
        status=ListingStatus.available,
        lat=payload.lat if payload.lat is not None else donor.lat,
        lng=payload.lng if payload.lng is not None else donor.lng,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return serialize_listing(listing)


def get_listing(db: Session, listing_id: int) -> ListingOut:
    listing = db.get(FoodListing, listing_id)
    if listing is None:
        raise NotFoundError(f"Listing {listing_id} not found")
    return serialize_listing(listing)


def list_listings(
    db: Session,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None,
    status: ListingStatus | None = ListingStatus.available,
    category: FoodCategory | None = None,
    limit: int = 100,
) -> list[ListingOut]:
    expire_stale(db)

    stmt = select(FoodListing).options(selectinload(FoodListing.donor))
    if status is not None:
        stmt = stmt.where(FoodListing.status == status)
    if category is not None:
        stmt = stmt.where(FoodListing.category == category)

    listings = db.execute(stmt).scalars().all()
    now = utcnow()
    origin = (lat, lng) if (lat is not None and lng is not None) else None
    out = [serialize_listing(listing, now, origin) for listing in listings]

    if origin is not None and radius_km is not None:
        out = [o for o in out if o.distance_km is not None and o.distance_km <= radius_km]

    # Most urgent first; break ties by nearest when a location is supplied.
    out.sort(key=lambda o: (-o.urgency.score, o.distance_km if o.distance_km is not None else 0.0))
    return out[:limit]


def list_donor_listings(db: Session, donor_id: int) -> list[ListingOut]:
    expire_stale(db)
    if db.get(Donor, donor_id) is None:
        raise NotFoundError(f"Donor {donor_id} not found")
    stmt = (
        select(FoodListing)
        .options(selectinload(FoodListing.donor))
        .where(FoodListing.donor_id == donor_id)
        .order_by(FoodListing.created_at.desc())
    )
    listings = db.execute(stmt).scalars().all()
    now = utcnow()
    return [serialize_listing(listing, now) for listing in listings]


def claim_listing(db: Session, listing_id: int, payload: ClaimRequest) -> PickupOut:
    listing = db.get(FoodListing, listing_id)
    if listing is None:
        raise NotFoundError(f"Listing {listing_id} not found")
    if listing.status != ListingStatus.available:
        raise ConflictError(f"Listing is '{listing.status.value}' and cannot be claimed")

    recipient = db.get(Recipient, payload.recipient_id)
    if recipient is None:
        raise NotFoundError(f"Recipient {payload.recipient_id} not found")

    pickup = Pickup(
        listing_id=listing.id,
        recipient_id=recipient.id,
        scheduled_at=as_utc(payload.scheduled_at) or utcnow(),
        servings_rescued=listing.servings,
    )
    listing.status = ListingStatus.claimed
    db.add(pickup)
    db.commit()
    db.refresh(pickup)

    return PickupOut(
        id=pickup.id,
        listing_id=pickup.listing_id,
        recipient_id=pickup.recipient_id,
        scheduled_at=pickup.scheduled_at,
        completed_at=pickup.completed_at,
        servings_rescued=pickup.servings_rescued,
        recipient=RecipientBrief.model_validate(recipient),
    )
