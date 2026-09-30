export default function SlotCard({ slot }) {
  return (
    <article className={`slot-card ${slot.occupied ? "is-occupied" : "is-free"}`}>
      <div className="slot-top">
        <span>{slot.name}</span>
        <span className="status-dot" />
      </div>
      <div className="parking-symbol">P</div>
      <h2>{slot.occupied ? "Occupied" : "Available"}</h2>
      <p>
        {slot.source || "sensor"} ·{" "}
        {slot.updated_at ? new Date(slot.updated_at).toLocaleTimeString() : "Waiting"}
      </p>
    </article>
  );
}
