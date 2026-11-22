import { useState, useEffect } from "react";
import { getBookings } from "./api.js";
import DateNav from "./components/DateNav.jsx";
import RoomList from "./components/RoomList.jsx";
import BookingList from "./components/BookingList.jsx";
import FindSlot from "./components/FindSlot.jsx";

const FIRST_SEEDED_DAY = "2026-12-07";

export default function App() {
  const [date, setDate] = useState(FIRST_SEEDED_DAY);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getBookings(date)
      .then((data) => {
        setBookings(data || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [date]);

  const handleBookingCreated = (newBooking) => {
    setBookings((prev) => [newBooking, ...prev]);
  };

  return (
    <main>
      <header>
        <div className="brand">
          <div className="brand-mark">RB</div>
          <h1>RoomBook</h1>
        </div>
        <DateNav date={date} onChange={setDate} />
      </header>
      <div className="layout">
        <RoomList />
        <BookingList date={date} bookings={bookings} loading={loading} error={error} />
      </div>
      <FindSlot date={date} onBookingCreated={handleBookingCreated} />
    </main>
  );
}
