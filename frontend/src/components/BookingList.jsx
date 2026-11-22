import { useEffect, useState } from "react";
import { getBookings } from "../api.js";
import { formatTime } from "../dates.js";
import BookingDetailModal from "./BookingDetailModal.jsx";

export default function BookingList({ date, bookings: propBookings, loading: propLoading, error: propError }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [bookings, setBookings] = useState(propBookings || []);
  const [localLoading, setLocalLoading] = useState(propLoading ?? true);
  const [localError, setLocalError] = useState(propError ?? null);

  // Sync with parent-provided bookings (real-time updates from slot booking)
  useEffect(() => {
    if (propBookings) {
      setBookings(propBookings);
    }
  }, [propBookings]);

  // Fetch from API on mount/date change (in case parent doesn't provide data)
  useEffect(() => {
    if (!propBookings) {
      setLocalLoading(true);
      setLocalError(null);
      getBookings(date)
        .then((data) => {
          setBookings(data || []);
          setLocalLoading(false);
        })
        .catch((err) => {
          setLocalError(err.message);
          setLocalLoading(false);
        });
    }
  }, [date, propBookings]);

  const loading = propLoading ?? localLoading;
  const error = propError ?? localError;
  const displayBookings = propBookings ?? bookings;

  return (
    <>
      <section className="card">
        <h2>Bookings for {date}</h2>
        {loading && <p className="muted">Loading…</p>}
        {error && <p className="error">{error}</p>}
        {!loading && !error && displayBookings.length === 0 && <p className="muted">No bookings.</p>}
        {displayBookings.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Room</th>
                <th>Title</th>
                <th>Attendees</th>
              </tr>
            </thead>
            <tbody>
              {displayBookings.map((b) => (
                <tr
                  key={b.id}
                  className="booking-row"
                  onClick={() => {
                    setSelectedBooking(b);
                    setModalOpen(true);
                  }}
                >
                  <td className="time-col">
                    {formatTime(b.start)}–{formatTime(b.end)}
                  </td>
                  <td className="room-col">{b.room.name}</td>
                  <td>{b.title}</td>
                  <td className="attendees-col">{b.attendees.map((a) => a.name).join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
      {modalOpen && selectedBooking && (
        <BookingDetailModal
          booking={selectedBooking}
          onClose={() => {
            setModalOpen(false);
            setSelectedBooking(null);
          }}
        />
      )}
    </>
  );
}
