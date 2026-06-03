import { describe, it, expect, beforeEach } from "vitest";
import {
  getToken,
  setToken,
  getUser,
  setUser,
  clearAuth,
  type AuthUser,
} from "@/lib/auth";

const sampleUser: AuthUser = {
  id: "u1",
  email: "ops@example.com",
  name: "Ops Manager",
  role: "admin",
};

beforeEach(() => {
  window.localStorage.clear();
});

describe("token helpers", () => {
  it("returns null when no token stored", () => {
    expect(getToken()).toBeNull();
  });

  it("round-trips a token", () => {
    setToken("abc.def.ghi");
    expect(getToken()).toBe("abc.def.ghi");
  });
});

describe("user helpers", () => {
  it("returns null when no user stored", () => {
    expect(getUser()).toBeNull();
  });

  it("round-trips a user object", () => {
    setUser(sampleUser);
    expect(getUser()).toEqual(sampleUser);
  });

  it("returns null when stored user is corrupt JSON", () => {
    window.localStorage.setItem("dclaw_fleet_user", "{not json");
    expect(getUser()).toBeNull();
  });
});

describe("clearAuth", () => {
  it("removes both token and user", () => {
    setToken("tok");
    setUser(sampleUser);
    clearAuth();
    expect(getToken()).toBeNull();
    expect(getUser()).toBeNull();
  });
});
