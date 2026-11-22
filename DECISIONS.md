# DECISIONS.md

## Task 1: Fix back-to-back bookings bug

**Bug:** `overlaps()` in `scheduling.py` used `<=` for endpoint comparison, so
a meeting ending at 11:00 was treated as clashing with one starting at 11:00.
Per the spec, times are half-open intervals, so back-to-back bookings should
be allowed.

**Fix:** Changed to strict `<` comparison: `a_start < b_end and b_start < a_end`.

**Test added:** `test_back_to_back_bookings_are_allowed` — books 11:30–12:00 in
Focus Room right after "Hiring panel" (10:00–11:30) ends.

**Other problems noticed in the codebase:**
- `create_booking` has a check-then-insert race condition: two concurrent
  requests can both pass the overlap check before either inserts. (Fixed in
  Task 3 with row-level locking.)
- **Fixed:** No validation that booking attendee count exceeds room capacity —
  now rejected with 400 in `create_booking` (see `test_exceeding_room_capacity_is_rejected`).
- No validation that booking start/end fall on 15-minute boundaries.
- No validation that booking duration is a multiple of 15 minutes (15–240).
- No validation that the booking is within working hours (09:30–18:30, Mon–Fri).
- No lunch-hour rule (no meeting may overlap 13:00–14:00 unless ≤30 min) on
  `POST /bookings` (only on `/suggest`).
- No cleaning buffer for meetings >60 min on `POST /bookings` (only on `/suggest`).
- No attendee conflict check across rooms at booking time (only room overlap)
  on `POST /bookings` (`/suggest` does check attendee conflicts).
- `simulated latency` middleware only delays GET requests; POST requests are
  instant, which doesn't reflect real network behavior for mutations.

## Task 2: POST /rooms/{room_id}/suggest

**Approach:** Generate all 15-minute boundary start times from 09:30 to
(18:30 − duration), then filter each candidate against all business rules.
Return the first 3 valid slots.

**Assumptions made where spec was unclear:**
- Working days are Monday–Friday only; weekends return an empty slot list.
- The `date` parameter is interpreted in IST (Asia/Kolkata, UTC+05:30).
- Output timestamps include the +05:30 offset.
- Lunch-hour rule: a meeting overlapping 13:00–14:00 is allowed only if its
  duration is ≤30 minutes (e.g. 12:45–13:15 is OK, 12:30–13:30 is not).
- Cleaning buffer applies only to room availability (not attendee availability),
  per the spec wording "during which the room can't be used."
- Intern restriction applies to both the requester and any attendee; if either
  is an intern and the room is the Board Room, no slots are returned.
- The requester is implicitly an attendee (added to the attendee set for
  conflict checking).

**Trade-offs:**
- Candidate slots are generated in Python rather than SQL, for clarity and
  portability across SQLite/PostgreSQL. For large scale, this could move to a
  stored procedure or a recursive CTE.
- Cleaning buffer for existing bookings >60 min blocks the room for 15 min
  after they end. This is applied only when checking room availability.

## Task 3: Prevent double booking

**Approach:** Row-level locking with `SELECT ... FOR UPDATE` on the room row
inside the booking transaction. The first transaction to lock the room checks
for overlaps and inserts; concurrent transactions block on the lock, then
re-check overlaps after the first commits and get a 409.

**Why this approach:** It works on both SQLite and PostgreSQL without needing
database-specific features like PostgreSQL's EXCLUDE constraint. It keeps the
logic in the application layer where it can be tested and maintained.

**Where it stops working:**
- Under very high contention, threads may pile up waiting for the row lock.
- It only serializes bookings for the same room; two users booking different
  rooms concurrently are unaffected (which is correct).
- If the application runs behind multiple workers without sticky sessions, the
  database lock still works correctly because it's at the DB level.
