def test_list_bookings_for_date(client):
    res = client.get("/bookings", params={"date": "2026-12-07"})
    assert res.status_code == 200
    bookings = res.json()
    assert len(bookings) == 8
    starts = [b["start"] for b in bookings]
    assert starts == sorted(starts)


def test_list_bookings_for_room(client):
    res = client.get("/bookings", params={"date": "2026-12-07", "room_id": 3})
    assert [b["title"] for b in res.json()] == ["Standup sync", "Retro"]


def test_create_booking(client):
    res = client.post(
        "/bookings",
        json={
            "room_id": 3,
            "creator_id": 2,
            "title": "Pairing",
            "attendee_ids": [2, 6],
            "start": "2026-12-07T15:00:00",
            "end": "2026-12-07T15:30:00",
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["room"]["name"] == "Huddle"
    assert {a["name"] for a in body["attendees"]} == {"Ben", "Farah"}


def test_overlapping_booking_is_rejected(client):
    res = client.post(
        "/bookings",
        json={
            "room_id": 1,
            "creator_id": 1,
            "attendee_ids": [1],
            "start": "2026-12-07T10:30:00",
            "end": "2026-12-07T11:00:00",
        },
    )
    assert res.status_code == 409


def test_back_to_back_bookings_are_allowed(client):
    """Back-to-back bookings (one ends exactly when the next starts) must not clash.

    Focus Room has "Hiring panel" 10:00-11:30 on 2026-12-07, so a booking
    starting at 11:30 (when it ends) must be accepted.
    """
    res = client.post(
        "/bookings",
        json={
            "room_id": 1,
            "creator_id": 1,
            "attendee_ids": [1],
            "start": "2026-12-07T11:30:00",
            "end": "2026-12-07T12:00:00",
        },
    )
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"


def test_end_must_be_after_start(client):
    res = client.post(
        "/bookings",
        json={
            "room_id": 1,
            "creator_id": 1,
            "start": "2026-12-07T11:00:00",
            "end": "2026-12-07T10:00:00",
        },
    )
    assert res.status_code == 422


def test_unknown_room(client):
    res = client.post(
        "/bookings",
        json={
            "room_id": 99,
            "creator_id": 1,
            "start": "2026-12-07T10:00:00",
            "end": "2026-12-07T11:00:00",
        },
    )
    assert res.status_code == 404


def test_unknown_attendee(client):
    res = client.post(
        "/bookings",
        json={
            "room_id": 3,
            "creator_id": 1,
            "attendee_ids": [42],
            "start": "2026-12-07T15:00:00",
            "end": "2026-12-07T15:30:00",
        },
    )
    assert res.status_code == 400


def test_suggest_basic(client):
    res = client.post(
        "/rooms/1/suggest",
        json={
            "requester_id": 1,
            "attendee_ids": [],
            "duration_minutes": 45,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["slots"]) <= 3
    starts = [s["start"] for s in body["slots"]]
    assert starts == sorted(starts)


def test_suggest_intern_cannot_book_board_room(client):
    res = client.post(
        "/rooms/2/suggest",
        json={
            "requester_id": 4,
            "attendee_ids": [],
            "duration_minutes": 30,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 200
    assert res.json()["slots"] == []


def test_suggest_weekend_returns_empty(client):
    res = client.post(
        "/rooms/1/suggest",
        json={
            "requester_id": 1,
            "attendee_ids": [],
            "duration_minutes": 30,
            "date": "2026-12-12",
        },
    )
    assert res.status_code == 200
    assert res.json()["slots"] == []


def test_suggest_attendee_conflict(client):
    # Chen (id 3) has "Hiring panel" 10:00-11:30 in Focus Room on 2026-12-07
    res = client.post(
        "/rooms/3/suggest",
        json={
            "requester_id": 1,
            "attendee_ids": [3],
            "duration_minutes": 30,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 200
    for slot in res.json()["slots"]:
        start = slot["start"][11:16]
        end = slot["end"][11:16]
        assert not (start < "11:30" and end > "10:00")


def test_suggest_lunch_long_meeting_rejected(client):
    res = client.post(
        "/rooms/1/suggest",
        json={
            "requester_id": 1,
            "attendee_ids": [],
            "duration_minutes": 45,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 200
    for slot in res.json()["slots"]:
        start = slot["start"][11:16]
        end = slot["end"][11:16]
        assert not (start < "14:00" and end > "13:00")


def test_suggest_room_not_found(client):
    res = client.post(
        "/rooms/99/suggest",
        json={
            "requester_id": 1,
            "attendee_ids": [],
            "duration_minutes": 30,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 404


def test_suggest_unknown_requester(client):
    res = client.post(
        "/rooms/1/suggest",
        json={
            "requester_id": 99,
            "attendee_ids": [],
            "duration_minutes": 30,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 404


def test_suggest_unknown_attendee(client):
    res = client.post(
        "/rooms/1/suggest",
        json={
            "requester_id": 1,
            "attendee_ids": [42],
            "duration_minutes": 30,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 400


def test_suggest_duration_too_short(client):
    res = client.post(
        "/rooms/1/suggest",
        json={
            "requester_id": 1,
            "attendee_ids": [],
            "duration_minutes": 10,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 422


def test_suggest_slot_times_have_ist_offset(client):
    res = client.post(
        "/rooms/1/suggest",
        json={
            "requester_id": 1,
            "attendee_ids": [],
            "duration_minutes": 30,
            "date": "2026-12-07",
        },
    )
    assert res.status_code == 200
    if res.json()["slots"]:
        assert "+05:30" in res.json()["slots"][0]["start"]


# ---- double-booking (concurrency) tests ----
