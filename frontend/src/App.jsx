import { useEffect, useState } from "react";
import { API_URL, fetchEvents, fetchSlots, fetchSummary, recommendSlot } from "./api";
import SlotCard from "./components/SlotCard";

export default function App() {
  const [slots, setSlots] = useState([]);
  const [summary, setSummary] = useState({ total: 0, occupied: 0, available: 0, occupancy_rate: 0 });
  const [events, setEvents] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    try {
      const [slotData, summaryData, eventData, recommendationData] = await Promise.all([
        fetchSlots(), fetchSummary(), fetchEvents(), recommendSlot(),
      ]);
      setSlots(slotData);
      setSummary(summaryData);
      setEvents(eventData);
      setRecommendation(recommendationData);
      setError("");
    } catch {
      setError("Backend unavailable. Start PostgreSQL, MQTT and the FastAPI server.");
    }
  };

  useEffect(() => {
    refresh();

    const socket = new WebSocket(API_URL.replace(/^http/, "ws") + "/ws");
    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onerror = () => setConnected(false);

    socket.onmessage = (message) => {
      const update = JSON.parse(message.data);
      if (update.type !== "slot_update") return;

      setSlots((current) => current.map((slot) =>
        slot.name === update.slot
          ? { ...slot, occupied: update.occupied, confidence: update.confidence, source: update.source, updated_at: update.updated_at }
          : slot
      ));

      setEvents((current) => [{
        id: Date.now(),
        slot_id: update.slot,
        occupied: update.occupied,
        source: update.source,
        confidence: update.confidence,
        created_at: update.updated_at,
      }, ...current].slice(0, 20));

      refresh();
    };

    return () => socket.close();
  }, []);

  return (
    <main className="page">
      <header className="header">
        <div>
          <p className="eyebrow">AI + IoT</p>
          <h1>Smart Parking System</h1>
          <p className="subtitle">Real-time monitoring, sensor fusion and parking analytics</p>
        </div>
        <span className={`connection ${connected ? "online" : "offline"}`}>
          {connected ? "● Live" : "○ Offline"}
        </span>
      </header>

      {error && <div className="alert">{error}</div>}

      <section className="summary">
        <div className="summary-card"><span>Total Slots</span><strong>{summary.total}</strong></div>
        <div className="summary-card available"><span>Available</span><strong>{summary.available}</strong></div>
        <div className="summary-card occupied"><span>Occupied</span><strong>{summary.occupied}</strong></div>
        <div className="summary-card"><span>Occupancy</span><strong>{summary.occupancy_rate.toFixed(1)}%</strong></div>
      </section>

      <section>
        <div className="section-heading">
          <h2>Live Parking Slots</h2>
          <button onClick={refresh}>Refresh</button>
        </div>
        <div className="slot-grid">
          {slots.map((slot) => <SlotCard key={slot.id} slot={slot} />)}
        </div>
      </section>

      <section className="recommendation">
        <h2>Smart Recommendation</h2>
        {recommendation
          ? <p>Recommended slot: <strong>{recommendation.slot_name}</strong> — {recommendation.reason}</p>
          : <p className="muted">No slot is currently available.</p>}
      </section>

      <section className="events">
        <div className="section-heading"><h2>Recent Events</h2></div>
        {events.length === 0 ? <p className="muted">No events yet.</p> : (
          <div className="event-list">
            {events.map((event) => (
              <div className="event-row" key={event.id}>
                <strong>{event.slot_id}</strong>
                <span>{event.occupied ? "Occupied" : "Available"}</span>
                <span>{event.source}</span>
                <span>{event.created_at ? new Date(event.created_at).toLocaleString() : ""}</span>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
