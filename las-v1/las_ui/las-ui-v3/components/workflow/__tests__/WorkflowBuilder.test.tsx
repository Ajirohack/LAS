import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { WorkflowBuilder } from "../WorkflowBuilder";
import { useAppStore } from "@/app/store";
import { Node } from "reactflow";

describe("WorkflowBuilder", () => {
  it("saves workflow to store when Save is clicked", async () => {
    useAppStore.setState({ workflows: [] });

    render(<WorkflowBuilder />);

    const saveButton = screen.getByRole("button", { name: /save/i });
    fireEvent.click(saveButton);

    const { workflows } = useAppStore.getState();
    expect(workflows.length).toBe(1);
    expect(workflows[0].nodes.length).toBeGreaterThan(0);
    expect(workflows[0].status).toBe("draft");
  });

  it("saves workflow with custom name", async () => {
    useAppStore.setState({ workflows: [] });
    render(<WorkflowBuilder />);
    const nameInput = screen.getByPlaceholderText(/workflow name/i);
    fireEvent.change(nameInput, { target: { value: "My Flow" } });
    const saveButton = screen.getByRole("button", { name: /save/i });
    fireEvent.click(saveButton);
    const { workflows } = useAppStore.getState();
    expect(workflows[0].name).toBe("My Flow");
  });

  it("loads workflow and sets name input", async () => {
    const nodes: Node[] = [
      {
        id: "x",
        type: "trigger",
        position: { x: 0, y: 0 },
        data: { label: "Start", type: "trigger" },
      },
    ];
    useAppStore.setState({
      workflows: [
        {
          id: "wf-1",
          name: "Loaded Flow",
          nodes,
          edges: [],
          status: "draft",
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ],
    });

    render(<WorkflowBuilder />);
    const loadButton = screen.getByRole("button", { name: /load/i });
    fireEvent.click(loadButton);
    const nameInput = screen.getByPlaceholderText(
      /workflow name/i
    ) as HTMLInputElement;
    expect(nameInput.value).toBe("Loaded Flow");
  });

  it("run updates execution metadata", async () => {
    useAppStore.setState({ workflows: [] });
    render(<WorkflowBuilder />);
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await new Promise((r) => setTimeout(r, 150));
    fireEvent.click(screen.getByRole("button", { name: /run/i }));
    await new Promise((r) => setTimeout(r, 2200));
    const { workflows } = useAppStore.getState();
    expect(workflows[0].lastRunStatus).toBe("success");
    expect(typeof workflows[0].lastRunDurationMs).toBe("number");
    expect((workflows[0].lastRunDurationMs || 0) >= 1900).toBe(true);
  });
});
