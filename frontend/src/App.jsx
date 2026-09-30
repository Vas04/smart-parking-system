import { useEffect, useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [slots, setSlots] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/api/slots`)
      .then((response) => response.json())
      .then(setSlots)
      .catch(() => setSlots([]));

    const wsUrl = API_URL.replace(/^http/, "ws") + "/ws";
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onmessage = (event) => {
      const update = JSON.parse(event.data);
      if (update.type !== "slot_update") return;
      setSlots((current) =>
        current.map((slot) =>
          slot.name === update.slot
            ? { ...slot, occupied: update.occupied, updated_at: update.updated_at }
            : slot
        )
      );
    };

    return () => socket.close();
  }, []);

  const occupied = useMemo(() => slots.filter((slot) => slot.occupied).length, [slots]);
  const available = slots.length - occupied;

  return (
    <main className="page">
      <header className="header">
        <div>
          <p className="eyebrow">AI + IoT</p>
          <h1>Smart Parking System</h1>
          <p className="subtitle">Real-time parking occupancy dashboard</p>
        </div>
        <span className={`connection ${connected ? "online" : "offline"}`}>
          {connected ? "● Live" : "○ Offline"}
        </span>
      </header>

      <section className="summary">
        <div className="summary-card">
          <span>Total Slots</span>
          <strong>{slots.length}</strong>
        </div>
        <div className="summary-card available">
          <span>Available</span>
          <strong>{available}</strong>
        </div>
        <div className="summary-card occupied">
          <span>Occupied</span>
          <strong>{occupied}</strong>
        </div>
      </section>

      <section className="slot-grid">
        {slots.map((slot) => (
          <article className={`slot-card ${slot.occupied ? "is-occupied" : "is-free"}`} key={slot.id}>
            <div className="slot-top">
              <span>{slot.name}</span>
              <span className="status-dot" />
            </div>
            <div className="parking-symbol">P</div>
            <h2>{slot.occupied ? "Occupied" : "Available"}</h2>
            <p>{slot.updated_at ? new Date(slot.updated_at).toLocaleTimeString() : "Waiting for data"}</p>
          </article>
        ))}
      </section>
    </main>
  );
}

export default App;
