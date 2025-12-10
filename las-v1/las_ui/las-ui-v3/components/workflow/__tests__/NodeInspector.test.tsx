import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import type { Node } from "reactflow";
import { NodeInspector } from "../NodeInspector";
import { describe, it, expect, vi } from "vitest";

// Mock the Node type since we don't have the full ReactFlow types in test context easily
// or we can just use a plain object that satisfies the shape we need.
const mockNode: Node = {
  id: "1",
  type: "trigger",
  position: { x: 0, y: 0 },
  data: {
    label: "Test Node",
    description: "A test description",
    config: { someKey: "someValue" },
  },
};

describe("NodeInspector", () => {
  it('renders "No node selected" when selectedNode is null', () => {
    render(<NodeInspector selectedNode={null} onUpdateNode={vi.fn()} />);
    expect(
      screen.getByText("Select a node to edit its properties")
    ).toBeInTheDocument();
  });

  it("renders form when a node is selected", () => {
    render(
      <NodeInspector selectedNode={mockNode} onUpdateNode={vi.fn()} />
    );
    expect(screen.getByDisplayValue("Test Node")).toBeInTheDocument();
    expect(screen.getByDisplayValue("A test description")).toBeInTheDocument();
  });

  it("calls onUpdateNode when form is submitted", async () => {
    const onUpdateNode = vi.fn();
    render(
      <NodeInspector
        selectedNode={mockNode}
        onUpdateNode={onUpdateNode}
      />
    );

    const labelInput = screen.getByDisplayValue("Test Node");
    fireEvent.change(labelInput, { target: { value: "Updated Node" } });

    const saveButton = screen.getByRole("button", { name: /save changes/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(onUpdateNode).toHaveBeenCalledWith(
        "1",
        expect.objectContaining({
          label: "Updated Node",
          description: "A test description",
        })
      );
    });
  });
});
