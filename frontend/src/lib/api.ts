import { clearAuth, getToken } from "@/lib/auth";

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
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string> | undefined),
  };
  const token = getToken();
  if (token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401 && !path.startsWith("/api/v1/auth/login")) {
    clearAuth();
    if (typeof window !== "undefined" && window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }
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
  external_id: string | null;
  synced_at: string | null;
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

// ── Auth ──
export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface MeResponse {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const auth = {
  login: (email: string, password: string) =>
    api<LoginResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => api<MeResponse>("/api/v1/auth/me"),
  register: (data: { email: string; password: string; name: string; role?: string }) =>
    api<MeResponse>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ── P1 domain types ──
export interface DrivingEvent {
  id: string;
  driver_id: string;
  vehicle_id: string;
  event_type: string;
  severity: number;
  lat: number | null;
  lng: number | null;
  recorded_at: string;
}

export interface DriverScore {
  driver_id: string;
  score: number;
  event_count: number;
  events_by_type: Record<string, number>;
}

export interface CoachingTip {
  event_type: string;
  severity: string;
  message: string;
}

export interface DriverCoaching {
  driver_id: string;
  score: number;
  tips: CoachingTip[];
}

export interface HOSLog {
  id: string;
  driver_id: string;
  vehicle_id: string | null;
  duty_status: string;
  started_at: string;
  ended_at: string | null;
  miles: number;
}

export interface HOSStatus {
  driver_id: string;
  current_status: string;
  on_duty_hours_today: number;
  driving_hours_today: number;
  remaining_drive_hours: number;
  remaining_duty_hours: number;
  violations: string[];
}

export interface DVIRReport {
  id: string;
  driver_id: string;
  vehicle_id: string;
  inspection_type: string;
  defects_count: number;
  notes: string | null;
  passed: boolean;
  submitted_at: string;
}

export interface Permit {
  id: string;
  entity_type: string;
  entity_id: string;
  permit_type: string;
  issuer: string | null;
  permit_number: string;
  issued_date: string | null;
  expiry_date: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ComplianceSummary {
  expired_permits: number;
  expiring_soon: number;
  failed_dvir: number;
  hos_violations: number;
}

export interface Expense {
  id: string;
  vehicle_id: string | null;
  driver_id: string | null;
  category: string;
  amount: number;
  vendor: string | null;
  expense_date: string;
  approval_status: string;
  approved_by: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExpenseAnalytics {
  total_amount: number;
  by_category: Record<string, number>;
  pending_approval_count: number;
  pending_approval_amount: number;
  flagged_count: number;
  flags: string[];
}

export interface RouteSyncResult {
  synced_count: number;
  failed_count: number;
  synced_route_ids: string[];
  synced_at: string;
}

export interface AutoAssignResult {
  assignments: { route_id: string; vehicle_id: string | null; vehicle_plate: string | null; reason: string }[];
  skipped_count: number;
  skipped_reasons: string[];
}

// ── P1 endpoints ──
export const drivingEvents = {
  list: (driverId?: string) =>
    api<DrivingEvent[]>(`/api/v1/driving-events${driverId ? `?driver_id=${driverId}` : ""}`),
  ingest: (data: Partial<DrivingEvent>) =>
    api<DrivingEvent>("/api/v1/driving-events", { method: "POST", body: JSON.stringify(data) }),
  score: (driverId: string) =>
    api<DriverScore>(`/api/v1/driving-events/drivers/${driverId}/score`),
  coaching: (driverId: string) =>
    api<DriverCoaching>(`/api/v1/driving-events/drivers/${driverId}/coaching`),
  recompute: (driverId: string) =>
    api<{ driver_id: string; safety_score: number }>(
      `/api/v1/driving-events/drivers/${driverId}/recompute-score`,
      { method: "POST" }
    ),
};

export const hos = {
  create: (data: Partial<HOSLog>) =>
    api<HOSLog>("/api/v1/hos-logs", { method: "POST", body: JSON.stringify(data) }),
  forDriver: (driverId: string) => api<HOSLog[]>(`/api/v1/hos-logs/drivers/${driverId}`),
  status: (driverId: string) =>
    api<HOSStatus>(`/api/v1/hos-logs/drivers/${driverId}/status`),
};

export const dvir = {
  list: () => api<DVIRReport[]>("/api/v1/dvir"),
  create: (data: Partial<DVIRReport>) =>
    api<DVIRReport>("/api/v1/dvir", { method: "POST", body: JSON.stringify(data) }),
  forVehicle: (vehicleId: string) =>
    api<DVIRReport[]>(`/api/v1/dvir/vehicles/${vehicleId}`),
};

export const permits = {
  list: () => api<Permit[]>("/api/v1/permits"),
  create: (data: Partial<Permit>) =>
    api<Permit>("/api/v1/permits", { method: "POST", body: JSON.stringify(data) }),
  expired: () => api<Permit[]>("/api/v1/permits/expired"),
  expiring: (days = 30) => api<Permit[]>(`/api/v1/permits/expiring?days=${days}`),
  summary: () => api<ComplianceSummary>("/api/v1/permits/compliance-summary"),
  remove: (id: string) => api<void>(`/api/v1/permits/${id}`, { method: "DELETE" }),
};

export const expenses = {
  list: () => api<Expense[]>("/api/v1/expenses"),
  create: (data: Partial<Expense>) =>
    api<Expense>("/api/v1/expenses", { method: "POST", body: JSON.stringify(data) }),
  pending: () => api<Expense[]>("/api/v1/expenses/pending"),
  analytics: () => api<ExpenseAnalytics>("/api/v1/expenses/analytics"),
  approve: (id: string, approved_by: string, approve: boolean) =>
    api<Expense>(`/api/v1/expenses/${id}/approve`, {
      method: "POST",
      body: JSON.stringify({ approved_by, approve }),
    }),
};

export const routeIntegration = {
  sync: () => api<RouteSyncResult>("/api/v1/route-integration/sync", { method: "POST" }),
  autoAssign: () =>
    api<AutoAssignResult>("/api/v1/route-integration/auto-assign", { method: "POST" }),
};

// ── P2 domain types ──
export interface ChargingSession {
  id: string;
  vehicle_id: string;
  station_id: string | null;
  started_at: string;
  ended_at: string | null;
  energy_kwh: number;
  cost: number;
  soc_start: number | null;
  soc_end: number | null;
}

export interface RangePrediction {
  vehicle_id: string;
  current_soc: number | null;
  estimated_range_miles: number;
  confidence: string;
  notes: string[];
}

export interface ChargeRecommendation {
  vehicle_id: string;
  needs_charge: boolean;
  target_soc: number;
  suggested_window: string;
  reason: string;
}

export interface AccidentReport {
  id: string;
  vehicle_id: string;
  driver_id: string | null;
  occurred_at: string;
  severity_score: number;
  photos_count: number;
  description: string | null;
  claim_status: string;
  claim_amount: number;
  predicted_claim_amount: number | null;
  lat: number | null;
  lng: number | null;
  created_at: string;
  updated_at: string;
}

export interface Part {
  id: string;
  name: string;
  sku: string;
  category: string;
  vendor: string | null;
  stock: number;
  reorder_threshold: number;
  unit_cost: number;
  created_at: string;
  updated_at: string;
}

export interface ReorderRecommendation {
  part_id: string;
  sku: string;
  name: string;
  current_stock: number;
  reorder_threshold: number;
  suggested_order_qty: number;
  estimated_cost: number;
}

export interface TelematicsDevice {
  id: string;
  vehicle_id: string;
  vendor: string;
  device_id: string;
  status: string;
  last_seen_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashcamEvent {
  id: string;
  vehicle_id: string;
  driver_id: string | null;
  event_type: string;
  severity: number;
  video_url: string | null;
  recorded_at: string;
}

export interface PartFailurePrediction {
  vehicle_id: string;
  component: string;
  probability: number;
  suggested_action: string;
  reason: string;
}

export interface PredictiveReport {
  vehicle_id: string;
  overall_risk: string;
  predictions: PartFailurePrediction[];
}

export interface CarbonReport {
  vehicle_id: string | null;
  co2_kg: number;
  fuel_gallons: number;
  miles: number;
  co2_per_mile_g: number;
  suggestions: string[];
}

export interface AutonomousDispatchResult {
  assignments: { route_id: string; vehicle_id: string; vehicle_plate: string; score: number }[];
  rejected: { route_id: string; reason: string }[];
  score: number;
}

// ── P2 endpoints ──
export const charging = {
  list: () => api<ChargingSession[]>("/api/v1/charging"),
  create: (data: Partial<ChargingSession>) =>
    api<ChargingSession>("/api/v1/charging", { method: "POST", body: JSON.stringify(data) }),
  forVehicle: (vehicleId: string) =>
    api<ChargingSession[]>(`/api/v1/charging/vehicles/${vehicleId}`),
  range: (vehicleId: string) =>
    api<RangePrediction>(`/api/v1/charging/vehicles/${vehicleId}/range`),
  recommendation: (vehicleId: string) =>
    api<ChargeRecommendation>(`/api/v1/charging/vehicles/${vehicleId}/recommendation`),
};

export const accidents = {
  list: () => api<AccidentReport[]>("/api/v1/accidents"),
  create: (data: Partial<AccidentReport>) =>
    api<AccidentReport>("/api/v1/accidents", { method: "POST", body: JSON.stringify(data) }),
  openClaims: () => api<AccidentReport[]>("/api/v1/accidents/open-claims"),
  update: (id: string, data: Partial<AccidentReport>) =>
    api<AccidentReport>(`/api/v1/accidents/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

export const parts = {
  list: () => api<Part[]>("/api/v1/parts"),
  create: (data: Partial<Part>) =>
    api<Part>("/api/v1/parts", { method: "POST", body: JSON.stringify(data) }),
  lowStock: () => api<Part[]>("/api/v1/parts/low-stock"),
  recommendations: () => api<ReorderRecommendation[]>("/api/v1/parts/reorder-recommendations"),
  update: (id: string, data: Partial<Part>) =>
    api<Part>(`/api/v1/parts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: string) => api<void>(`/api/v1/parts/${id}`, { method: "DELETE" }),
};

export const telematics = {
  devices: () => api<TelematicsDevice[]>("/api/v1/telematics/devices"),
  registerDevice: (data: Partial<TelematicsDevice>) =>
    api<TelematicsDevice>("/api/v1/telematics/devices", { method: "POST", body: JSON.stringify(data) }),
  heartbeat: (device_id: string, payload: Record<string, any>) =>
    api<{ device_id: string; vehicle_id: string; anomalies: string[] }>(
      "/api/v1/telematics/heartbeat",
      { method: "POST", body: JSON.stringify({ device_id, payload }) }
    ),
};

export const dashcam = {
  list: () => api<DashcamEvent[]>("/api/v1/dashcam"),
  create: (data: Partial<DashcamEvent>) =>
    api<DashcamEvent>("/api/v1/dashcam", { method: "POST", body: JSON.stringify(data) }),
  forVehicle: (vehicleId: string) =>
    api<DashcamEvent[]>(`/api/v1/dashcam/vehicles/${vehicleId}`),
};

export const predictive = {
  maintenance: (vehicleId: string) =>
    api<PredictiveReport>(`/api/v1/predictive/maintenance/vehicles/${vehicleId}`),
  carbonVehicle: (vehicleId: string) =>
    api<CarbonReport>(`/api/v1/predictive/carbon/vehicles/${vehicleId}`),
  carbonFleet: () => api<CarbonReport>("/api/v1/predictive/carbon/fleet"),
  dispatchPlan: () =>
    api<AutonomousDispatchResult>("/api/v1/predictive/dispatch/plan", { method: "POST" }),
};

// ── Back-compat type stubs (legacy callers) ──
export type FleetStatus = any;
export type VehicleStatus = any;
