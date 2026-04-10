import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

function HomeStub() {
  return <h1>Knowledge and Insight Workspace</h1>;
}

describe("Home page", () => {
  it("renders core heading", () => {
    render(<HomeStub />);
    expect(
      screen.getByText("Knowledge and Insight Workspace"),
    ).toBeInTheDocument();
  });
});
