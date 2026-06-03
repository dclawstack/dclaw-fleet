import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { api, getHealth, ApiError } from "@/lib/api";
import { getToken } from "@/lib/auth";

function mockFetch(response: Partial<Response> & { status: number }) {
  const fn = vi.fn().mockResolvedValue({
    ok: response.status >= 200 && response.status < 300,
    status: response.status,
    json: response.json ?? (async () => ({})),
    text: response.text ?? (async () => ""),
  } as Response);
  vi.stubGlobal("fetch", fn);
  return fn;
}

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchJson", () => {
  it("returns parsed JSON on a 200", async () => {
    mockFetch({ status: 200, json: async () => ({ hello: "world" }) });
    await expect(api<{ hello: string }>("/x")).resolves.toEqual({ hello: "world" });
  });

  it("sets a JSON content-type and no auth header when no token", async () => {
    const fetchFn = mockFetch({ status: 200, json: async () => ({}) });
    await api("/x");
    const headers = fetchFn.mock.calls[0][1].headers as Record<string, string>;
    expect(headers["Content-Type"]).toBe("application/json");
    expect(headers["Authorization"]).toBeUndefined();
  });

  it("attaches a Bearer token from storage", async () => {
    window.localStorage.setItem("dclaw_fleet_token", "tok123");
    const fetchFn = mockFetch({ status: 200, json: async () => ({}) });
    await api("/x");
    const headers = fetchFn.mock.calls[0][1].headers as Record<string, string>;
    expect(headers["Authorization"]).toBe("Bearer tok123");
  });

  it("does not override a caller-supplied Authorization header", async () => {
    window.localStorage.setItem("dclaw_fleet_token", "tok123");
    const fetchFn = mockFetch({ status: 200, json: async () => ({}) });
    await api("/x", { headers: { Authorization: "Bearer custom" } });
    const headers = fetchFn.mock.calls[0][1].headers as Record<string, string>;
    expect(headers["Authorization"]).toBe("Bearer custom");
  });

  it("returns undefined for a 204 No Content", async () => {
    mockFetch({ status: 204 });
    await expect(api("/x")).resolves.toBeUndefined();
  });

  it("throws ApiError carrying the status on a non-ok response", async () => {
    mockFetch({ status: 500, text: async () => "boom" });
    await expect(api("/x")).rejects.toMatchObject({
      name: "Error",
      status: 500,
    });
    await expect(api("/x")).rejects.toBeInstanceOf(ApiError);
  });

  it("clears auth on a 401 from a non-login path", async () => {
    window.localStorage.setItem("dclaw_fleet_token", "tok123");
    // Keep pathname === "/login" so the redirect branch is skipped in jsdom.
    window.history.replaceState({}, "", "/login");
    mockFetch({ status: 401, text: async () => "unauthorized" });
    await expect(api("/protected")).rejects.toBeInstanceOf(ApiError);
    expect(getToken()).toBeNull();
  });
});

describe("getHealth", () => {
  it("calls the health endpoint", async () => {
    const fetchFn = mockFetch({ status: 200, json: async () => ({ status: "ok" }) });
    await expect(getHealth()).resolves.toEqual({ status: "ok" });
    expect(fetchFn.mock.calls[0][0]).toContain("/health/");
  });
});
