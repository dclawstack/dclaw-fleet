const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (response.status === 204) {
    return undefined as unknown as T;
  }
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(`API error ${response.status}: ${error}`, response.status);
  }
  return response.json();
}

export const api = fetchJson;

export async function getHealth() {
  return fetchJson<{ status: string }>("/health/");
}

// ── Domain types ──
export interface Page<T> {
  items: T[];
  meta: { total: number; limit: number; offset: number };
}

export interface Vehicle {
  id: string;
  vin: string;
  license_plate: string;
  make: string;
  model: string;
  year: number;
  status: string;
  fuel_type: string;
  odometer_miles: number;
  engine_hours: number;
  driver_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Driver {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  license_number: string;
  license_expiry: string | null;
  status: string;
  safety_score: number;
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  name: string;
  asset_type: string;
  serial_number: string | null;
  status: string;
  location: string | null;
  created_at: string;
  updated_at: string;
}

export interface Geofence {
  id: string;
  name: string;
  fence_type: string;
  center_lat: number;
  center_lng: number;
  radius_m: number;
  created_at: string;
  updated_at: string;
}

export interface LocationPing {
  id: string;
  vehicle_id: string;
  lat: number;
  lng: number;
  speed_mph: number;
  heading_deg: number;
  recorded_at: string;
}

export interface MaintenanceTask {
  id: string;
  vehicle_id: string;
  task_type: string;
  description: string | null;
  due_date: string | null;
  due_mileage: number | null;
  status: string;
  completed_date: string | null;
  cost: number | null;
  created_at: string;
  updated_at: string;
}

export interface FuelLog {
  id: string;
  vehicle_id: string;
  driver_id: string | null;
  gallons: number;
  cost: number;
  odometer_miles: number;
  fuel_type: string;
  filled_at: string;
  created_at: string;
  updated_at: string;
}

export interface FuelReport {
  vehicle_id: string;
  total_gallons: number;
  total_cost: number;
  total_miles: number;
  mpg: number | null;
  anomalies: string[];
}

export interface Route {
  id: string;
  name: string;
  status: string;
  vehicle_id: string | null;
  optimized_distance_miles: number | null;
  optimized_duration_min: number | null;
  stops: RouteStop[];
  created_at: string;
  updated_at: string;
}

export interface RouteStop {
  id: string;
  route_id: string;
  sequence: number;
  address: string;
  lat: number;
  lng: number;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface ChatTurn {
  session_id: string;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  suggested_actions: string[];
}

// ── Domain endpoints ──
export const vehicles = {
  list: () => api<Page<Vehicle>>("/api/v1/vehicles"),
  create: (data: Partial<Vehicle>) =>
    api<Vehicle>("/api/v1/vehicles", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Vehicle>) =>
    api<Vehicle>(`/api/v1/vehicles/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: string) => api<void>(`/api/v1/vehicles/${id}`, { method: "DELETE" }),
};

export const drivers = {
  list: () => api<Page<Driver>>("/api/v1/drivers"),
  create: (data: Partial<Driver>) =>
    api<Driver>("/api/v1/drivers", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Driver>) =>
    api<Driver>(`/api/v1/drivers/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: string) => api<void>(`/api/v1/drivers/${id}`, { method: "DELETE" }),
};

export const assets = {
  list: () => api<Page<Asset>>("/api/v1/assets"),
  create: (data: Partial<Asset>) =>
    api<Asset>("/api/v1/assets", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Asset>) =>
    api<Asset>(`/api/v1/assets/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: string) => api<void>(`/api/v1/assets/${id}`, { method: "DELETE" }),
};

export const geofences = {
  list: () => api<Page<Geofence>>("/api/v1/geofences"),
  create: (data: Partial<Geofence>) =>
    api<Geofence>("/api/v1/geofences", { method: "POST", body: JSON.stringify(data) }),
  remove: (id: string) => api<void>(`/api/v1/geofences/${id}`, { method: "DELETE" }),
};

export const tracking = {
  latest: () => api<LocationPing[]>("/api/v1/locations/latest"),
  history: (vehicleId: string) =>
    api<LocationPing[]>(`/api/v1/locations/vehicles/${vehicleId}/history`),
  ingest: (data: { vehicle_id: string; lat: number; lng: number; speed_mph?: number }) =>
    api<{ ping: LocationPing; breach_alerts: any[] }>("/api/v1/locations/ingest", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export const maintenance = {
  list: () => api<Page<MaintenanceTask>>("/api/v1/maintenance"),
  create: (data: Partial<MaintenanceTask>) =>
    api<MaintenanceTask>("/api/v1/maintenance", { method: "POST", body: JSON.stringify(data) }),
  overdue: () => api<MaintenanceTask[]>("/api/v1/maintenance/overdue"),
  forVehicle: (vehicleId: string) =>
    api<MaintenanceTask[]>(`/api/v1/maintenance/vehicles/${vehicleId}`),
  healthScore: (vehicleId: string) =>
    api<{ vehicle_id: string; health_score: number }>(
      `/api/v1/maintenance/vehicles/${vehicleId}/health-score`
    ),
  autoSchedule: (vehicleId: string) =>
    api<MaintenanceTask | null>(
      `/api/v1/maintenance/vehicles/${vehicleId}/auto-schedule`,
      { method: "POST" }
    ),
  update: (id: string, data: Partial<MaintenanceTask>) =>
    api<MaintenanceTask>(`/api/v1/maintenance/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

export const fuel = {
  list: () => api<Page<FuelLog>>("/api/v1/fuel-logs"),
  create: (data: Partial<FuelLog>) =>
    api<FuelLog>("/api/v1/fuel-logs", { method: "POST", body: JSON.stringify(data) }),
  report: (vehicleId: string) =>
    api<FuelReport>(`/api/v1/fuel-logs/vehicles/${vehicleId}/report`),
};

export const routes = {
  list: () => api<Page<Route>>("/api/v1/routes"),
  create: (data: { name: string; stops: Omit<RouteStop, "id" | "route_id">[] }) =>
    api<Route>("/api/v1/routes", { method: "POST", body: JSON.stringify(data) }),
  optimize: (id: string) =>
    api<Route>(`/api/v1/routes/${id}/optimize`, { method: "POST" }),
  remove: (id: string) => api<void>(`/api/v1/routes/${id}`, { method: "DELETE" }),
};

export const fleetAi = {
  chat: (message: string, session_id?: string) =>
    api<ChatTurn>("/api/v1/ai/chat", {
      method: "POST",
      body: JSON.stringify({ message, session_id }),
    }),
};

// ── Back-compat type stubs (legacy callers) ──
export type FleetStatus = any;
export type VehicleStatus = any;
