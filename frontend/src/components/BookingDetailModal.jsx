import { formatTime } from "../dates.js";

export default function BookingDetailModal({ booking, onClose }) {
  if (!booking) return null;

  const room = booking.room;
  const startDate = new Date(booking.start).toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button
          className="modal-close"
          type="button"
          aria-label="Close"
          onClick={onClose}
        >
          ✕
        </button>

        <div className="modal-header">
          <h2 className="modal-title">{booking.title || "Untitled Booking"}</h2>
          <span className="modal-badge">
            {room?.name || "Unknown Room"}
          </span>
        </div>

        <div className="modal-section">
          <h3 className="modal-section-title">Details</h3>
          <div className="detail-row">
            <span className="detail-label">Room</span>
            <span className="detail-value">
              {room?.name || "Unknown"} ({room?.capacity ?? "?"} seats)
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Date</span>
            <span className="detail-value">{startDate}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Time</span>
            <span className="detail-value">
              {formatTime(booking.start)} – {formatTime(booking.end)}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Created by</span>
            <span className="detail-value">
              {booking.creator?.name || booking.creator_id}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Attendees</span>
            <span className="detail-value">
              {booking.attendees?.map((a) => a.name).join(", ") || "None"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}