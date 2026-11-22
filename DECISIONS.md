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
  requests can both pass the overlap check before either inserts. (Not fixed
  in this PR — planned for the prevent-double-booking PR.)
- No validation that booking attendee count exceeds room capacity (not fixed
  in this PR — planned for a follow-up).
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
