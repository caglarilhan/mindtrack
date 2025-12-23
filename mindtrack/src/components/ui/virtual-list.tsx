"use client";

import * as React from "react";
import { FixedSizeList, ListChildComponentProps } from "react-window";

interface VirtualListProps<T> {
  items: T[];
  height: number;
  itemHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  className?: string;
}

/**
 * Virtual scrolling list component
 * Use for large lists (100+ items) to improve performance
 */
export function VirtualList<T>({
  items,
  height,
  itemHeight,
  renderItem,
  className,
}: VirtualListProps<T>) {
  const Row = React.useCallback(
    ({ index, style }: ListChildComponentProps) => (
      <div style={style}>{renderItem(items[index], index)}</div>
    ),
    [items, renderItem]
  );

  return (
    <FixedSizeList
      height={height}
      itemCount={items.length}
      itemSize={itemHeight}
      width="100%"
      className={className}
    >
      {Row}
    </FixedSizeList>
  );
}





