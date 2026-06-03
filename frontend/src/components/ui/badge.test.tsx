import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Badge } from "@/components/ui/badge";

describe("Badge", () => {
  it("renders its content", () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("uses the default variant classes", () => {
    render(<Badge>Default</Badge>);
    expect(screen.getByText("Default").className).toContain("bg-primary");
  });

  it("applies the destructive variant", () => {
    render(<Badge variant="destructive">Overdue</Badge>);
    expect(screen.getByText("Overdue").className).toContain("bg-destructive");
  });

  it("merges a custom className", () => {
    render(<Badge className="custom-x">X</Badge>);
    expect(screen.getByText("X").className).toContain("custom-x");
  });
});
