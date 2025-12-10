import { render, screen, fireEvent } from "@testing-library/react";
import { Sidebar } from "../Sidebar";
import { useAppStore } from "@/app/store";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { useRouter } from "next/navigation";

// Mock dependencies
vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {
    return;
  }
  unobserve() {
    return;
  }
  disconnect() {
    return;
  }
};

describe("Sidebar", () => {
  beforeEach(() => {
    useAppStore.setState({
      sessions: [
        {
          id: "1",
          title: "Test Session",
          timestamp: new Date(),
          messageCount: 5,
          lastMessage: "Hello world",
        },
      ],
      workspaces: [
        { id: "default", name: "Default", color: "#000", isActive: true },
      ],
      currentSessionId: "1",
      currentWorkspaceId: "default",
    });

    vi.mocked(useRouter).mockReturnValue({
      push: vi.fn(),
    } as unknown as ReturnType<typeof useRouter>);
  });

  it("renders session list", () => {
    render(<Sidebar />);
    expect(screen.getByText("Test Session")).toBeInTheDocument();
    expect(screen.getByText("Hello world")).toBeInTheDocument();
  });

  it("renders workspace switcher", () => {
    render(<Sidebar />);
    expect(screen.getByText("Default")).toBeInTheDocument();
  });

  it("allows searching sessions", () => {
    render(<Sidebar />);
    const searchInput = screen.getByPlaceholderText("Search sessions...");
    fireEvent.change(searchInput, { target: { value: "Test" } });
    expect(screen.getByText("Test Session")).toBeInTheDocument();

    fireEvent.change(searchInput, { target: { value: "Nonexistent" } });
    expect(screen.queryByText("Test Session")).not.toBeInTheDocument();
  });

  it("navigates when clicking items", () => {
    const pushMock = vi.fn();
    vi.mocked(useRouter).mockReturnValue({
      push: pushMock,
    } as unknown as ReturnType<typeof useRouter>);

    render(<Sidebar />);
    fireEvent.click(screen.getByText("Workflows"));
    expect(pushMock).toHaveBeenCalledWith("/workflow");
  });
});
