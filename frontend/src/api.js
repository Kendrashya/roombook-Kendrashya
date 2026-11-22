const BASE = "/api";

async function request(path, options) {
  const res = await fetch(BASE + path, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : null;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const getRooms = () => request("/rooms");

export const getUsers = () => request("/users");

export const getBookings = (date, roomId) => {
  let url = `/bookings?date=${date}`;
  if (roomId) url += `&room_id=${roomId}`;
  return request(url);
};

export const createBooking = (booking) =>
  request("/bookings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(booking),
  });

export const suggestSlots = (roomId, body) =>
  request(`/rooms/${roomId}/suggest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

export const getRoom = (id) => request(`/rooms/${id}`);
