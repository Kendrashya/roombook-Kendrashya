import { useState, useEffect, useRef } from "react";

export default function AttendeeSelect({ users, value, onChange, disabled }) {
  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState("");
  const containerRef = useRef(null);
  const selectedIds = new Set(value || []);

  const available = users.filter(
    (u) => !selectedIds.has(String(u.id)) && u.name.toLowerCase().includes(filter.toLowerCase())
  );

  // Close dropdown when clicking outside the component
  useEffect(() => {
    const handleClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const toggle = (id) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onChange(Array.from(next));
    setFilter("");
    setIsOpen(false);
  };

  const remove = (id) => {
    const next = new Set(selectedIds);
    next.delete(id);
    onChange(Array.from(next));
  };

  return (
    <div ref={containerRef} className="attendee-select" onClick={(e) => e.stopPropagation()}>
      <label className="field-label">Attendees</label>

      {/* Selected chips */}
      <div className="chips">
        {users
          .filter((u) => selectedIds.has(String(u.id)))
          .map((u) => (
            <span key={u.id} className="chip">
              {u.name}
              <button
                type="button"
                className="chip-remove"
                aria-label={`Remove ${u.name}`}
                onClick={(e) => {
                  e.stopPropagation();
                  remove(String(u.id));
                }}
              >
                ×
              </button>
            </span>
          ))}
        {!disabled && (
          <button
            type="button"
            className="chip-add"
            aria-label="Add attendees"
            onClick={(e) => {
              e.stopPropagation();
              setIsOpen(!isOpen);
            }}
          >
            {isOpen ? "▲" : "+ Attendees"}
          </button>
        )}
      </div>

      {/* Dropdown */}
      {!disabled && isOpen && (
        <div className="dropdown">
          <input
            className="select search"
            type="text"
            placeholder="Search attendees…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            autoFocus
          />
          {available.length === 0 ? (
            <div className="dropdown-empty">No matching attendees</div>
          ) : (
            available.map((u) => (
              <button
                key={u.id}
                type="button"
                className={`dropdown-item ${selectedIds.has(String(u.id)) ? "selected" : ""}`}
                onClick={(e) => {
                  e.stopPropagation();
                  toggle(String(u.id));
                }}
              >
                <span className="item-name">{u.name}</span>
                <span className="item-role muted">{u.role}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}