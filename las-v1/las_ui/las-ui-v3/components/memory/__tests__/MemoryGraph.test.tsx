import { render } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MemoryGraph, MemoryGraphData } from "../MemoryGraph";

describe("MemoryGraph", () => {
  const data: MemoryGraphData = {
    nodes: [
      {
        id: "a",
        label: "A",
        type: "concept",
        category: "cat",
        importance: 0.5,
        confidence: 0.7,
        timestamp: new Date("2024-01-01"),
      },
      {
        id: "b",
        label: "B",
        type: "entity",
        category: "cat",
        importance: 0.4,
        confidence: 0.6,
        timestamp: new Date("2024-01-02"),
      },
    ],
    links: [{ source: "a", target: "b", type: "related", strength: 0.8 }],
  };

  it("renders svg container", () => {
    render(<MemoryGraph data={data} width={400} height={300} />);
    const svgEl = document.querySelector("svg");
    expect(svgEl).toBeTruthy();
  });
});
