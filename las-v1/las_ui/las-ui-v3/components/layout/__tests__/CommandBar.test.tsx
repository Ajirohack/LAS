import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { CommandBar } from '../CommandBar';

// Mock useRouter
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock useAppStore
const mockUseAppStore = vi.fn();
vi.mock('@/app/store', () => ({
  useAppStore: () => mockUseAppStore(),
}));

// Mock ResizeObserver
beforeEach(() => {
  // @ts-expect-error jsdom does not implement ResizeObserver
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

describe('CommandBar', () => {
  const defaultStore = {
    commandBarOpen: true,
    openCommandBar: vi.fn(),
    closeCommandBar: vi.fn(),
    toggleCommandBar: vi.fn(),
    sessions: [],
    recentCommands: [],
    addRecentCommand: vi.fn(),
    setActivePanel: vi.fn(),
    setTheme: vi.fn(),
    theme: 'dark',
  };

  beforeEach(() => {
    mockUseAppStore.mockReturnValue(defaultStore);
    mockPush.mockClear();
    vi.clearAllMocks();
  });

  it('renders command bar when open', () => {
    render(<CommandBar />);
    expect(screen.getByPlaceholderText('Type a command or search...')).toBeInTheDocument();
  });

  it('does not render command bar content when closed', () => {
    mockUseAppStore.mockReturnValue({
      ...defaultStore,
      commandBarOpen: false,
    });
    render(<CommandBar />);
    expect(screen.queryByPlaceholderText('Type a command or search...')).not.toBeInTheDocument();
  });

  it('navigates to chat when selected', () => {
    render(<CommandBar />);
    // We might need to look for the item text. 
    // Depending on cmdk implementation, it might need to be filtered first or just exist.
    // Assuming standard rendering:
    const chatOption = screen.getByText('Go to Chat');
    fireEvent.click(chatOption);
    
    expect(defaultStore.setActivePanel).toHaveBeenCalledWith('chat');
    expect(mockPush).toHaveBeenCalledWith('/');
    expect(defaultStore.closeCommandBar).toHaveBeenCalled();
  });

  it('toggles theme', () => {
    render(<CommandBar />);
    const themeOption = screen.getByText('Toggle Theme');
    fireEvent.click(themeOption);
    
    expect(defaultStore.setTheme).toHaveBeenCalledWith('light');
    expect(defaultStore.closeCommandBar).toHaveBeenCalled();
  });

  it('handles keyboard shortcut to toggle', () => {
    render(<CommandBar />);
    fireEvent.keyDown(window, { key: 'k', metaKey: true });
    expect(defaultStore.toggleCommandBar).toHaveBeenCalled();
  });
});
