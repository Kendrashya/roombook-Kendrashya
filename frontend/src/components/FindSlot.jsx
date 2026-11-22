import { useState, useEffect } from "react";
import { getRooms, getUsers, suggestSlots, createBooking } from "../api.js";
import { formatTime } from "../dates.js";
import AttendeeSelect from "./AttendeeSelect.jsx";

const DURATION_OPTIONS = [15, 30, 45, 60, 90, 120, 180, 240];

export default function FindSlot({ date, onBookingCreated }) {
  const [rooms, setRooms] = useState([]);
  const [users, setUsers] = useState([]);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [suggestLoading, setSuggestLoading] = useState(false);
  const [error, setError] = useState(null);
  const [booked, setBooked] = useState(null);

  const [roomId, setRoomId] = useState("");
  const [attendeeIds, setAttendeeIds] = useState([]);
  const [duration, setDuration] = useState("30");

  useEffect(() => {
    getRooms().then(setRooms).catch((err) => setError(err.message));
    getUsers().then(setUsers).catch((err) => setError(err.message));
  }, []);

  const handleSuggest = async (e) => {
    e.preventDefault();
    setError(null);
    setSlots([]);
    setBooked(null);
    setSuggestLoading(true);

    try {
      const body = {
        requester_id: Number(attendeeIds[0] || 1),
        attendee_ids: attendeeIds.map(Number),
        duration_minutes: Number(duration),
        date,
      };
      const data = await suggestSlots(roomId, body);
      setSlots(data.slots || []);
    } catch (err) {
      setError(err.message || "Failed to find slots");
    } finally {
      setSuggestLoading(false);
    }
  };

  const handleBook = async (slot) => {
    setLoading(true);
    setError(null);
    try {
      const newBooking = await createBooking({
        room_id: Number(roomId),
        creator_id: Number(attendeeIds[0] || 1),
        title: "Booked from slot suggestion",
        attendee_ids: attendeeIds.map(Number),
        start: slot.start,
        end: slot.end,
      });
      setBooked(slot);
      setSlots([]);
      // Notify parent to update the booking table in real-time
      if (onBookingCreated && newBooking) {
        onBookingCreated(newBooking);
      }
    } catch (err) {
      if (err.message && err.message.includes("409")) {
        setError("This slot was taken by someone else. Please choose another.");
      } else {
        setError(err.message || "Failed to book slot");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>Find a slot</h2>
      {error && <div className="alert alert-error">{error}</div>}
      {booked && (
        <div className="alert alert-success">
          ✅ Booked {formatTime(booked.start)}–{formatTime(booked.end)}
        </div>
      )}
      <form onSubmit={handleSuggest} className="slot-form">
        <label>
          Room
          <select
            className="select"
            value={roomId}
            onChange={(e) => setRoomId(e.target.value)}
            disabled={suggestLoading}
          >
            <option value="">Select a room</option>
            {rooms.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} ({r.capacity} seats)
              </option>
            ))}
          </select>
        </label>
        <AttendeeSelect
          users={users}
          value={attendeeIds}
          onChange={setAttendeeIds}
          disabled={suggestLoading}
        />
        <label>
          Duration (min)
          <select className="select" value={duration} onChange={(e) => setDuration(e.target.value)} disabled={suggestLoading}>
            {DURATION_OPTIONS.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </label>
        <label>
          Date
          <div className="date-picker">
            <span className="muted">{date}</span>
          </div>
        </label>
        <button
          type="submit"
          className="btn btn-primary btn-full"
          disabled={!roomId || suggestLoading}
        >
          {suggestLoading ? "Finding…" : "Find slots"}
        </button>
      </form>

      {slots.length > 0 && (
        <div className="slot-section">
          <h3>Suggested slots</h3>
          <div className="slot-grid">
            {slots.map((slot, i) => (
              <button
                key={i}
                className={`slot-card ${loading ? "disabled" : ""}`}
                onClick={() => handleBook(slot)}
                disabled={loading}
              >
                <span className="slot-time">{formatTime(slot.start)}</span>
                <span className="slot-range">{formatTime(slot.end)}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}