const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export const fetchSlots = () => request("/api/slots");
export const fetchSummary = () => request("/api/summary");
export const fetchEvents = () => request("/api/events?limit=20");
export const recommendSlot = () => request("/api/recommendation");

export { API_URL };
