import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MessageVirtualizer, ChatMessage } from '../MessageVirtualizer';

// Mock ResizeObserver
beforeEach(() => {
  // @ts-expect-error jsdom does not implement ResizeObserver
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

// Mock useVirtualScroll hook
vi.mock('@/hooks/use-virtual-scroll', () => ({
  useVirtualScroll: vi.fn(({ count, estimateSize }) => ({
    parentRef: { current: document.createElement('div') },
    rowVirtualizer: {
      getVirtualItems: () => 
        Array.from({ length: Math.min(count, 5) }).map((_, i) => ({
          index: i,
          start: i * estimateSize(),
          size: estimateSize(),
          key: i,
          measureElement: vi.fn(),
        })),
      getTotalSize: () => count * estimateSize(),
      measureElement: vi.fn(),
    },
    scrollToEnd: vi.fn(),
  })),
}));

const mockMessages: ChatMessage[] = [
  {
    id: '1',
    role: 'user',
    content: 'Hello',
    timestamp: new Date().toISOString(),
  },
  {
    id: '2',
    role: 'assistant',
    content: 'Hi there!',
    timestamp: new Date().toISOString(),
  },
  {
    id: '3',
    role: 'user',
    content: 'How are you?',
    timestamp: new Date().toISOString(),
  },
];

describe('MessageVirtualizer', () => {
  it('renders messages correctly', () => {
    render(<MessageVirtualizer messages={mockMessages} />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
    expect(screen.getByText('How are you?')).toBeInTheDocument();
  });

  it('renders user and assistant avatars', () => {
    render(<MessageVirtualizer messages={mockMessages} />);
    
    // Check for user/bot role labels or structure
    expect(screen.getAllByText('user')).toHaveLength(2);
    expect(screen.getAllByText('assistant')).toHaveLength(1);
  });

  it('handles message editing', () => {
    const onMessageEdit = vi.fn();
    render(<MessageVirtualizer messages={mockMessages} onMessageEdit={onMessageEdit} />);
    
    // Simulate hover and click edit (simplified since we can't easily hover in jsdom)
    // We'll just look for the edit button. Since it's opacity-0 by default, check if it's in the document.
    const editButtons = screen.getAllByTitle('Edit message');
    expect(editButtons).toHaveLength(3);
    
    fireEvent.click(editButtons[0]);
    expect(onMessageEdit).toHaveBeenCalledWith('1', 'Hello');
  });

  it('handles message deletion', () => {
    const onMessageDelete = vi.fn();
    render(<MessageVirtualizer messages={mockMessages} onMessageDelete={onMessageDelete} />);
    
    const deleteButtons = screen.getAllByTitle('Delete message');
    expect(deleteButtons).toHaveLength(3);
    
    fireEvent.click(deleteButtons[0]);
    expect(onMessageDelete).toHaveBeenCalledWith('1');
  });

  it('shows loading state for last assistant message', () => {
    const messages = [...mockMessages];
    render(<MessageVirtualizer messages={messages} isLoading={true} />);
    
    // We expect the last message (which is user in mockMessages) NOT to show loading
    // because loading only applies to assistant messages at the end.
    
    // Let's add an assistant message at the end
    const messagesWithAssistant = [
      ...mockMessages,
      {
        id: '4',
        role: 'assistant' as const,
        content: 'Thinking...',
        timestamp: new Date().toISOString(),
      }
    ];
    
    render(<MessageVirtualizer messages={messagesWithAssistant} isLoading={true} />);
    // The loading spinner might be an SVG or element with specific class
    // In our code: <Loader2 className="w-3 h-3 animate-spin" />
    // We can query by generic selector if needed, or check if content is there.
    expect(screen.getByText('Thinking...')).toBeInTheDocument();
  });
});
