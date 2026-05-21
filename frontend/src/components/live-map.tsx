"use client";

import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, Circle } from "react-leaflet";
import L from "leaflet";

import { geofences, tracking, vehicles, type Geofence, type LocationPing, type Vehicle } from "@/lib/api";

// Fix Leaflet default-icon path issue with bundlers.
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: () => string })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

export function LiveMap() {
  const [pings, setPings] = useState<LocationPing[]>([]);
  const [vs, setVs] = useState<Vehicle[]>([]);
  const [fences, setFences] = useState<Geofence[]>([]);

  async function refresh() {
    try {
      const [p, v, f] = await Promise.all([tracking.latest(), vehicles.list(), geofences.list()]);
      setPings(p);
      setVs(v.items);
      setFences(f.items);
    } catch (e) {
      console.error(e);
    }
  }

  useEffect(() => {
    refresh();
    const i = setInterval(refresh, 10_000);
    return () => clearInterval(i);
  }, []);

  const center: [number, number] =
    pings.length > 0
      ? [pings[0].lat, pings[0].lng]
      : fences.length > 0
        ? [fences[0].center_lat, fences[0].center_lng]
        : [37.7749, -122.4194];

  return (
    <div className="overflow-hidden rounded-xl border bg-white">
      <MapContainer center={center} zoom={11} style={{ height: "70vh", width: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {fences.map((f) => (
          <Circle
            key={f.id}
            center={[f.center_lat, f.center_lng]}
            radius={f.radius_m}
            pathOptions={{
              color: f.fence_type === "exclusion" ? "#dc2626" : "#2563eb",
              fillOpacity: 0.1,
            }}
          >
            <Popup>{f.name} ({f.fence_type})</Popup>
          </Circle>
        ))}
        {pings.map((p) => {
          const veh = vs.find((v) => v.id === p.vehicle_id);
          return (
            <Marker key={p.id} position={[p.lat, p.lng]}>
              <Popup>
                <div className="text-xs">
                  <div className="font-semibold">{veh ? `${veh.license_plate} — ${veh.make} ${veh.model}` : p.vehicle_id}</div>
                  <div>{p.speed_mph.toFixed(0)} mph · heading {p.heading_deg.toFixed(0)}°</div>
                  <div className="text-slate-500">{new Date(p.recorded_at).toLocaleString()}</div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
      <div className="border-t bg-slate-50 px-4 py-2 text-xs text-slate-500">
        Showing {pings.length} live vehicle{pings.length === 1 ? "" : "s"} and {fences.length} geofence{fences.length === 1 ? "" : "s"}. Polls every 10s.
      </div>
    </div>
  );
}
