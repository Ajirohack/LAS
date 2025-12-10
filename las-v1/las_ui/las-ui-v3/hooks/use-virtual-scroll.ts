import { useRef, useCallback, useEffect } from "react";
import { useVirtualizer, VirtualizerOptions } from "@tanstack/react-virtual";

type PartialKeys<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

interface UseVirtualScrollOptions<TItemElement extends Element>
  extends Omit<
    PartialKeys<
      VirtualizerOptions<HTMLDivElement, TItemElement>,
      "observeElementRect" | "observeElementOffset" | "scrollToFn"
    >,
    "getScrollElement"
  > {
  count: number;
  estimateSize: (index: number) => number;
  overscan?: number;
  /**
   * If true, will automatically scroll to bottom when count increases
   */
  autoScroll?: boolean;
}

export function useVirtualScroll<TItemElement extends Element = HTMLElement>({
  count,
  estimateSize,
  overscan = 5,
  autoScroll = false,
  ...options
}: UseVirtualScrollOptions<TItemElement>) {
  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count,
    getScrollElement: () => parentRef.current,
    estimateSize,
    overscan,
    ...options,
  });

  const scrollToEnd = useCallback(
    (smooth = false) => {
      if (!parentRef.current) return;

      try {
        rowVirtualizer.scrollToIndex(count - 1, {
          align: "end",
          behavior: smooth ? "smooth" : "auto",
        });
      } catch {
        // Fallback
        if (parentRef.current) {
          parentRef.current.scrollTop = parentRef.current.scrollHeight;
        }
      }
    },
    [count, rowVirtualizer]
  );

  // Handle auto-scrolling when count changes
  useEffect(() => {
    if (!autoScroll || count === 0) return;

    // We use a small timeout to ensure the new item is rendered/measured
    const timeoutId = setTimeout(() => {
      scrollToEnd(true);
    }, 50);

    return () => clearTimeout(timeoutId);
  }, [count, autoScroll, scrollToEnd]);

  return {
    parentRef,
    rowVirtualizer,
    scrollToEnd,
  };
}
