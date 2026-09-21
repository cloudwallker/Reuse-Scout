// SYNTHETIC ONLY. No CSV export implementation.
export type Row = { label: string; count: number };
export function visibleRows(rows: Row[]): Row[] {
  return rows.filter(row => row.count > 0);
}
