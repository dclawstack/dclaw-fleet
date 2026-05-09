# DClaw Fleet — v1.2 Feature Roadmap

> Based on: Y Combinator vertical SaaS principles, trending GitHub repos (traccar, fleet-management), AI product research (Samsara, Motive, Verizon Connect, Geotab)

## Pre-Flight Checklist

- [ ] `frontend/package-lock.json` committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks correct
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [ ] Vehicle/asset registry
- [ ] GPS tracking & maps
- [ ] Maintenance scheduling
- [ ] Driver management
- [ ] Real backend CRUD (no mocks)
- [ ] Docker + Helm deployment
- [ ] Alembic migrations
- [ ] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have (Ship in v1.0, demo-ready)

#### 1. AI Fleet Copilot (Operations Commander)
**Description:** AI assistant that monitors fleet health, suggests route changes, and answers operational questions. "Which driver is closest to the emergency delivery?"
- **AI Angle:** Real-time data + RAG over fleet policies. LLM-powered decision support.
- **Backend:** `/api/v1/ai/fleet-chat` endpoint. Real-time telemetry ingestion.
- **Frontend:** AI panel with map overlay and proactive alerts.
- **Files:** `backend/app/services/fleet_ai.py`, `frontend/src/components/fleet-copilot.tsx`

#### 2. Real-Time GPS Tracking & Geofencing
**Description:** Live vehicle locations on map. Geofence alerts for entry/exit/dwell.
- **Backend:** GPS data ingestion (MQTT/websocket). Geofence engine.
- **Frontend:** Live map with vehicle icons. Geofence editor.
- **Files:** `backend/app/services/tracking.py`, `frontend/src/app/fleet/map.tsx`

#### 3. Route Optimization & Dispatch
**Description:** AI-optimized routes considering traffic, delivery windows, vehicle capacity, and driver hours.
- **AI Angle:** OR-Tools / VRP solver. Real-time traffic integration.
- **Backend:** Route optimization API. Dispatch engine.
- **Frontend:** Route planner with drag-and-drop stops. ETA predictions.
- **Files:** `backend/app/services/route_optimizer.py`

#### 4. Preventive Maintenance Scheduling
**Description:** Schedule maintenance based on mileage, engine hours, or time. Alert on overdue items.
- **Backend:** Maintenance scheduler. Work order generation.
- **Frontend:** Maintenance calendar. Vehicle health scorecards.
- **Files:** `backend/app/services/maintenance.py`

### P1 — Should Have (v1.1–1.2)

#### 5. Driver Behavior & Safety Scoring
**Description:** Track harsh braking, speeding, idle time. AI safety score with coaching tips.
- **AI Angle:** Telematics anomaly detection. Safety scoring model.
- **Backend:** Behavior analysis pipeline.
- **Frontend:** Driver scorecards. Safety trend charts.

#### 6. Fuel Management & Optimization
**Description:** Track fuel consumption, identify inefficiencies, find cheapest fuel stops on route.
- **Backend:** Fuel data integration. Cost analysis.
- **Frontend:** Fuel dashboard. Route fuel cost estimator.

#### 7. Compliance & ELD Integration
**Description:** Electronic logging device integration. HOS compliance tracking. DVIR reports.
- **Backend:** ELD data ingestion. HOS calculation engine.
- **Frontend:** Driver logs. Compliance status dashboard.

#### 8. Asset & Equipment Tracking
**Description:** Track non-vehicle assets (trailers, containers, tools) with IoT tags.
- **Backend:** Asset registry + location history.
- **Frontend:** Asset map. Utilization reports.

### P2 — Could Have (v1.3+)

#### 9. Predictive Maintenance (AI)
**Description:** AI predicts component failures before they happen using telematics patterns.

#### 10. Autonomous Fleet Dispatch
**Description:** AI auto-dispatch system that assigns jobs to optimal vehicles in real-time.

#### 11. Carbon Emission Tracking
**Description:** Track and report fleet carbon footprint. Suggest eco-routing.

#### 12. Video Telematics & AI Dashcams
**Description:** AI-powered dashcams that detect collisions, distracted driving, and road events.

---

## Implementation Priority

1. **Week 1–2:** AI Fleet Copilot (P0.1) + GPS Tracking (P0.2)
2. **Week 3–4:** Route Optimization (P0.3) + Maintenance Scheduling (P0.4)
3. **Week 5–6:** Driver Safety (P1.5) + Fuel Management (P1.6)
4. **Week 7–8:** ELD Compliance (P1.7) + Asset Tracking (P1.8)
