import { useState } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  flexRender,
} from "@tanstack/react-table";
import type { ColumnDef, SortingState } from "@tanstack/react-table";

interface DataTableProps<TData> {
  columns: ColumnDef<TData, any>[];
  data: TData[];
  searchPlaceholder?: string;
  onRowClick?: (row: TData) => void;
  exportFileName?: string;
}

export function DataTable<TData>({
  columns,
  data,
  searchPlaceholder = "Search record...",
  onRowClick,
  exportFileName = "report",
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [columnVisibility, setColumnVisibility] = useState({});

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter,
      columnVisibility,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    globalFilterFn: "includesString",
  });

  const exportToCSV = () => {
    if (!data.length) return;
    
    // Extract headers
    const headers = columns
      .map((col) => (col.header as string) || col.id || "")
      .filter((h) => h !== "");
      
    // Map rows to match headers
    const rows = data.map((item: any) =>
      columns
        .map((col) => {
          const accessor = (col as any).accessorKey || col.id;
          if (typeof accessor === "string") {
            return `"${(item[accessor] ?? "").toString().replace(/"/g, '""')}"`;
          }
          return '""';
        })
        .join(",")
    );

    const csvContent = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${exportFileName}_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="table-container-card">
      <div className="table-controls-bar">
        {/* Search */}
        <div className="table-search-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={globalFilter ?? ""}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="table-search-input"
          />
        </div>

        {/* Action controls */}
        <div className="table-actions-wrapper">
          {/* Column selector */}
          <div className="column-dropdown-container">
            <button className="btn-table-control">
              <span>🎛️</span> Columns
            </button>
            <div className="column-dropdown">
              {table.getAllLeafColumns().map((column: any) => (
                <label key={column.id} className="column-checkbox-label">
                  <input
                    type="checkbox"
                    checked={column.getIsVisible()}
                    onChange={column.getToggleVisibilityHandler()}
                  />
                  <span>{column.id.replace(/_/g, " ")}</span>
                </label>
              ))}
            </div>
          </div>

          {/* CSV Export */}
          <button className="btn-table-control" onClick={exportToCSV}>
            <span>📤</span> Export CSV
          </button>
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table>
          <thead>
            {table.getHeaderGroups().map((headerGroup: any) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header: any) => (
                  <th
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    style={{ cursor: header.column.getCanSort() ? "pointer" : "default" }}
                  >
                    <div className="th-content">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === "asc" ? " 🔼" : header.column.getIsSorted() === "desc" ? " 🔽" : ""}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row: any) => (
              <tr
                key={row.id}
                onClick={() => onRowClick && onRowClick(row.original)}
                style={{ cursor: onRowClick ? "pointer" : "default" }}
              >
                {row.getVisibleCells().map((cell: any) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
            {table.getRowModel().rows.length === 0 && (
              <tr>
                <td colSpan={columns.length} style={{ textAlign: "center", padding: "40px 24px", color: "var(--text-secondary)" }}>
                  No data available for the selected filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination controls */}
      {table.getPageCount() > 1 && (
        <div className="table-pagination">
          <div className="pagination-info">
            Page <strong>{table.getState().pagination.pageIndex + 1}</strong> of <strong>{table.getPageCount()}</strong>
          </div>
          <div className="pagination-buttons">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="btn-paginate"
            >
              Previous
            </button>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="btn-paginate"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
