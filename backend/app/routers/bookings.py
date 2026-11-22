from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Booking, Room, User
from ..scheduling import overlaps
from ..schemas import BookingIn, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingOut])
def list_bookings(
    date: date | None = None,
    room_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = (
        select(Booking)
        .options(selectinload(Booking.attendees), selectinload(Booking.room))
        .order_by(Booking.start)
    )
    if date is not None:
        day_start = datetime.combine(date, time.min)
        query = query.where(Booking.start >= day_start, Booking.start < day_start + timedelta(days=1))
    if room_id is not None:
        query = query.where(Booking.room_id == room_id)
    return db.scalars(query).all()


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingIn, db: Session = Depends(get_db)):
    room = db.get(Room, payload.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if db.get(User, payload.creator_id) is None:
        raise HTTPException(status_code=404, detail="Creator not found")

    attendee_ids = set(payload.attendee_ids)
    attendees = db.scalars(select(User).where(User.id.in_(attendee_ids))).all()
    if len(attendees) != len(attendee_ids):
        raise HTTPException(status_code=400, detail="Unknown attendee")

    # Capacity check: total unique people (creator + attendees) must not exceed
    # the room's capacity.
    total_people = attendee_ids | {payload.creator_id}
    if len(total_people) > room.capacity:
        raise HTTPException(
            status_code=400,
            detail=f"Room capacity is {room.capacity}, but {len(total_people)} people would attend",
        )

    # Lock the room row to serialize concurrent booking attempts for the same
    # room. This prevents two overlapping bookings from both succeeding when
    # submitted at the same moment: the second transaction waits for the first
    # to commit, then re-checks overlaps and gets a 409.
    db.execute(select(Room).where(Room.id == room.id).with_for_update())
    db.flush()

    existing = db.scalars(select(Booking).where(Booking.room_id == room.id)).all()
    for other in existing:
        if overlaps(other.start, other.end, payload.start, payload.end):
            raise HTTPException(status_code=409, detail="Room is already booked for that time")

    booking = Booking(
        room_id=room.id,
        creator_id=payload.creator_id,
        title=payload.title,
        start=payload.start,
        end=payload.end,
        attendees=list(attendees),
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking
