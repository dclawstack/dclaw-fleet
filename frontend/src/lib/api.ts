export interface FleetStatus {
  id: string;
  fleet_id: string;
  active_vehicles: number;
  avg_fuel_efficiency: number;
  maintenance_due_count: number;
  route_compliance_percent: number;
  created_at: string;
}

export interface VehicleStatus {
  vehicle_id: string;
  driver: string;
  status: string;
  location: string;
}

export async function api<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const url = `/api/v1${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };

  const res = await fetch(url, {
    ...init,
    headers,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json() as Promise<T>;
}
