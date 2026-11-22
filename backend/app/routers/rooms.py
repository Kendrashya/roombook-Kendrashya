from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Booking, Room, User
from ..scheduling import overlaps
from ..schemas import RoomIn, RoomOut, SuggestIn, SuggestOut, SlotOut

router = APIRouter(prefix="/rooms", tags=["rooms"])

IST_OFFSET = timezone(timedelta(hours=5, minutes=30))
WORK_START = time(9, 30)
WORK_END = time(18, 30)
LUNCH_START = time(13, 0)
LUNCH_END = time(14, 0)
CLEANING_BUFFER_MIN = 15
MAX_SUGGESTIONS = 3


@router.get("", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.scalars(select(Room).order_by(Room.id)).all()


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("", response_model=RoomOut, status_code=201)
def create_room(payload: RoomIn, db: Session = Depends(get_db)):
    room = Room(name=payload.name, capacity=payload.capacity)
    db.add(room)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A room with that name already exists")
    return room


@router.post("/{room_id}/suggest", response_model=SuggestOut)
def suggest_slots(
    room_id: int,
    payload: SuggestIn,
    db: Session = Depends(get_db),
):
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if db.get(User, payload.requester_id) is None:
        raise HTTPException(status_code=404, detail="Requester not found")

    # --- validate date ---
    try:
        day = date.fromisoformat(payload.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date (use YYYY-MM-DD)")

    # Working days only: Monday-Friday
    if day.weekday() >= 5:
        return SuggestOut(slots=[])

    # --- intern restriction on Board Room ---
    def _is_intern(uid: int) -> bool:
        u = db.get(User, uid)
        return u is not None and u.role == "intern"

    restricted = room.name == "Board Room" and (
        _is_intern(payload.requester_id)
        or any(_is_intern(aid) for aid in payload.attendee_ids)
    )
    if restricted:
        return SuggestOut(slots=[])

    # --- validate attendees exist ---
    attendee_ids = set(payload.attendee_ids)
    attendee_ids.add(payload.requester_id)
    attendees = db.scalars(select(User).where(User.id.in_(attendee_ids))).all()
    if len(attendees) != len(attendee_ids):
        raise HTTPException(status_code=400, detail="Unknown attendee")

    # --- load existing bookings ---
    room_bookings = db.scalars(select(Booking).where(Booking.room_id == room_id)).all()
    attendee_bookings = (
        db.scalars(select(Booking).options(selectinload(Booking.attendees))).all()
    )
    attendee_booking_list = [
        b for b in attendee_bookings if any(a.id in attendee_ids for a in b.attendees)
    ]

    # --- generate candidate slots ---
    duration = timedelta(minutes=payload.duration_minutes)
    slot_start = datetime.combine(day, WORK_START)
    last_start = datetime.combine(day, WORK_END) - duration
    candidates = []
    while slot_start <= last_start:
        candidates.append((slot_start, slot_start + duration))
        slot_start += timedelta(minutes=15)

    # --- filter candidates ---
    valid = []
    for s_start, s_end in candidates:
        # Lunch hour: no meeting may overlap 13:00-14:00 unless <= 30 min
        lunch_start_dt = datetime.combine(day, LUNCH_START)
        lunch_end_dt = datetime.combine(day, LUNCH_END)
        if overlaps(s_start, s_end, lunch_start_dt, lunch_end_dt) and payload.duration_minutes > 30:
            continue

        # Room has no overlapping booking (with cleaning buffer for long meetings)
        room_free = True
        for b in room_bookings:
            b_start, b_end = b.start, b.end
            if overlaps(s_start, s_end, b_start, b_end):
                room_free = False
                break
            if (b_end - b_start) > timedelta(minutes=60):
                buffer_end = b_end + timedelta(minutes=CLEANING_BUFFER_MIN)
                if overlaps(s_start, s_end, b_end, buffer_end):
                    room_free = False
                    break
        if not room_free:
            continue

        # No attendee has an overlapping booking in any room
        attendee_free = True
        for b in attendee_booking_list:
            if overlaps(s_start, s_end, b.start, b.end):
                attendee_free = False
                break
        if not attendee_free:
            continue

        valid.append((s_start, s_end))
        if len(valid) >= MAX_SUGGESTIONS:
            break

    # --- format output ---
    out_slots = []
    for s_start, s_end in valid:
        start_ist = s_start.replace(tzinfo=IST_OFFSET)
        end_ist = s_end.replace(tzinfo=IST_OFFSET)
        out_slots.append(SlotOut(start=start_ist.isoformat(), end=end_ist.isoformat()))

    return SuggestOut(slots=out_slots)
