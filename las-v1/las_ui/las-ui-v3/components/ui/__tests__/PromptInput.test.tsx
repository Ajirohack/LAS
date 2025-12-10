import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { PromptInput } from "../prompt-input";

// Mock the hooks
const mockHandleFileUpload = vi.fn();
const mockStartRecording = vi.fn();
const mockStopRecording = vi.fn();
const mockClearRecording = vi.fn();
const mockRemoveBlock = vi.fn();

vi.mock("@/hooks/use-file-upload", () => ({
  useFileUpload: () => ({
    contentBlocks: [],
    handleFileUpload: mockHandleFileUpload,
    removeBlock: mockRemoveBlock,
    handlePaste: vi.fn(),
    dropRef: { current: null },
    dragOver: false,
    fileCount: 0,
    isAtLimit: false,
  }),
}));

vi.mock("@/hooks/use-voice-recording", () => ({
  useVoiceRecording: () => ({
    isRecording: false,
    isSupported: true,
    startRecording: mockStartRecording,
    stopRecording: mockStopRecording,
    recordingTime: 0,
    audioBlob: null,
    clearRecording: mockClearRecording,
    error: null,
  }),
}));

describe("PromptInput", () => {
  const defaultProps = {
    value: "",
    onChange: vi.fn(),
    onSubmit: vi.fn(),
    isLoading: false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders input area correctly", () => {
    render(<PromptInput {...defaultProps} />);
    expect(screen.getByPlaceholderText(/Send a message/i)).toBeInTheDocument();
  });

  it("handles text input", () => {
    render(<PromptInput {...defaultProps} />);
    const textarea = screen.getByPlaceholderText(
      /Send a message/i
    ) as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "Hello" } });
    expect(textarea.value).toBe("Hello");
  });

  it("submits on enter key", () => {
    render(<PromptInput {...defaultProps} />);
    const textarea = screen.getByPlaceholderText(/Send a message/i);
    fireEvent.change(textarea, { target: { value: "Hello" } });
    fireEvent.keyDown(textarea, {
      key: "Enter",
      code: "Enter",
      shiftKey: false,
    });
    expect(defaultProps.onSubmit).toHaveBeenCalled();
  });

  it("does not submit on shift+enter", () => {
    render(<PromptInput {...defaultProps} value="Hello" />);
    const textarea = screen.getByPlaceholderText(/Send a message/i);
    fireEvent.keyDown(textarea, {
      key: "Enter",
      code: "Enter",
      shiftKey: true,
    });
    expect(defaultProps.onSubmit).not.toHaveBeenCalled();
  });

  it("shows file upload button", () => {
    render(<PromptInput {...defaultProps} />);
    const uploadBtn = screen.getByLabelText(/Attach file/i); // Assuming aria-label or title
    expect(uploadBtn).toBeInTheDocument();
  });

  it("shows voice recording button when supported", () => {
    render(<PromptInput {...defaultProps} />);
    const micBtn = screen.getByLabelText(/Start recording/i);
    expect(micBtn).toBeInTheDocument();
  });

  it("calls startRecording when mic button clicked", () => {
    render(<PromptInput {...defaultProps} />);
    const micBtn = screen.getByLabelText(/Start recording/i);
    fireEvent.click(micBtn);
    expect(mockStartRecording).toHaveBeenCalled();
  });
});
