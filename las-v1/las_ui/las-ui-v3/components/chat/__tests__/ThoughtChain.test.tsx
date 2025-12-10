import { render, screen, fireEvent } from "@testing-library/react";
import { ThoughtChain, ThoughtStep } from "../ThoughtChain";
import { describe, it, expect } from "vitest";

describe("ThoughtChain", () => {
  const mockSteps: ThoughtStep[] = [
    {
      id: "step-1",
      type: "reasoning",
      title: "Analyzing input",
      content: "User asked about weather",
      timestamp: new Date(),
      status: "completed",
      duration: 150,
    },
    {
      id: "step-2",
      type: "tool_call",
      title: "Calling weather API",
      content: "Fetching data for London",
      timestamp: new Date(),
      status: "running",
      tool: {
        name: "weather_api",
        input: { city: "London" },
      },
    },
  ];

  it("renders thought steps", () => {
    render(<ThoughtChain steps={mockSteps} />);
    expect(screen.getByText("Analyzing input")).toBeInTheDocument();
    expect(screen.getByText("Calling weather API")).toBeInTheDocument();
  });

  it("shows thinking badge when active", () => {
    render(<ThoughtChain steps={mockSteps} isActive={true} />);
    expect(screen.getByText("Thinking")).toBeInTheDocument();
  });

  it("expands step details on click", () => {
    render(<ThoughtChain steps={mockSteps} />);

    // Initially content is not visible (unless expanded by default? No, default is collapsed)
    const stepHeader = screen.getByText("Analyzing input");
    fireEvent.click(stepHeader);

    expect(screen.getByText("User asked about weather")).toBeInTheDocument();
  });

  it("shows tool details when expanded", () => {
    render(<ThoughtChain steps={mockSteps} />);

    const stepHeader = screen.getByText("Calling weather API");
    fireEvent.click(stepHeader);

    expect(screen.getByText("weather_api")).toBeInTheDocument();
    expect(screen.getByText(/"city": "London"/)).toBeInTheDocument();
  });

  it("toggles global details view", () => {
    render(<ThoughtChain steps={mockSteps} />);

    const toggleButton = screen.getByText("Show Details");
    fireEvent.click(toggleButton);

    expect(screen.getByText("Hide Details")).toBeInTheDocument();
  });
});
