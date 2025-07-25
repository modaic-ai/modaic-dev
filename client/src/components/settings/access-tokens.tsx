import {
  Plus,
  MoreHorizontal,
  Key,
  Info,
  ArrowUpDown,
  ChevronDown,
  ArrowDownUp,
  CopyIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import * as React from "react";
import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";

// Token type definition
type Token = {
  id: string;
  name: string;
  value: string;
  "last Refreshed": string;
  "last Used": string;
  permissions: string[];
};

// Sample data for demonstration
const sampleTokens: Token[] = [
  {
    id: "1",
    name: "modaic-local",
    value: "hf_...Ksij",
    "last Refreshed": "less than a minute ago",
    "last Used": "-",
    permissions: ["READ"],
  },
  {
    id: "2",
    name: "test-token",
    value: "hf_...NQRJ",
    "last Refreshed": "about 5 hours ago",
    "last Used": "-",
    permissions: ["WRITE"],
  },
];

export const columns: ColumnDef<Token>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
        className="cursor-pointer"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
        className="cursor-pointer"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="flex items-center gap-2"
        >
          Name
          {column.getIsSorted() === "asc" ? (
            <ArrowDownUp size={16} />
          ) : (
            <ArrowDownUp size={16} />
          )}
        </Button>
      );
    },
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <Key className="w-4 h-4 text-gray-400" />
        <span className="font-medium">{row.getValue("name")}</span>
      </div>
    ),
  },
  {
    accessorKey: "value",
    header: "Value",
    cell: ({ row }) => (
      <code className="text-gray-300 font-mono text-sm bg-gray-700 px-2 py-1 rounded">
        {row.getValue("value")}
      </code>
    ),
  },
  {
    accessorKey: "last Refreshed",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="flex items-center gap-2"
        >
          Last Refreshed Date
          {column.getIsSorted() === "asc" ? (
            <ArrowDownUp size={16} />
          ) : (
            <ArrowDownUp size={16} />
          )}
        </Button>
      );
    },
    cell: ({ row }) => <div>{row.getValue("last Refreshed")}</div>,
  },
  {
    accessorKey: "last Used",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="flex items-center gap-2"
        >
          Last Used Date
          {column.getIsSorted() === "asc" ? (
            <ArrowDownUp size={16} />
          ) : (
            <ArrowDownUp size={16} />
          )}
        </Button>
      );
    },
    cell: ({ row }) => <div>{row.getValue("last Used")}</div>,
  },
  {
    accessorKey: "permissions",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="flex items-center gap-2"
        >
          Permissions
          {column.getIsSorted() === "asc" ? (
            <ArrowDownUp size={16} />
          ) : (
            <ArrowDownUp size={16} />
          )}
        </Button>
      );
    },
    cell: ({ row }) => {
      const permissions = row.getValue("permissions") as string[];
      return (
        <div className="flex gap-1">
          {permissions.map((permission: string) => (
            <span
              key={permission}
              className={`text-white text-xs px-1 py-0.5 rounded font-semibold ${
                permission === "READ" ? "bg-gray-600" : "bg-orange-500"
              }`}
            >
              {permission}
            </span>
          ))}
        </div>
      );
    },
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const token = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="p-0">
            <DropdownMenuLabel className="text-muted-foreground font-semibold border-b w-full m-0">
              Actions
            </DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() => navigator.clipboard.writeText(token.value)}
              className="text-muted-foreground"
            >
              <CopyIcon size={12} /> Copy token value
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-muted-foreground">
              Edit token
            </DropdownMenuItem>
            <DropdownMenuItem className="text-muted-foreground">
              Delete token
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

function TokensTable({ tokens }: { tokens: Token[] }) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  );
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});

  const table = useReactTable({
    data: tokens,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  });

  return (
    <div className="w-full">
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter token names..."
          value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("name")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="ml-auto">
              Columns <ChevronDown className="ml-2" size={16} />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter((column) => column.getCanHide())
              .map((column) => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize cursor-pointer hover:bg-accent"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) =>
                      column.toggleVisibility(!!value)
                    }
                  >
                    {column.id}
                  </DropdownMenuCheckboxItem>
                );
              })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <div className="overflow-hidden rounded-md border">
        <Table>
          <TableHeader className="bg-transparent hover:bg-transparent">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead
                      className="bg-transparent hover:bg-transparent"
                      key={header.id}
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="hover:bg-border cursor-pointer"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="text-muted-foreground flex-1 text-sm">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}

function AccessTokensTab() {
  const [plusOrientation1, setPlusOrientation1] = React.useState(0);
  const [plusOrientation2, setPlusOrientation2] = React.useState(0);

  // Use sample tokens for demonstration - replace with your actual token data
  const tokens = sampleTokens;

  return (
    <div>
      <div className="max-w-7xl mx-auto">
        {/* User Access Tokens Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-medium">Your Access Tokens</h2>
            <Button
              onMouseEnter={() => setPlusOrientation1(45)}
              onMouseLeave={() => setPlusOrientation1(0)}
              className="px-4 py-2 rounded-md flex items-center gap-1 transition-colors"
            >
              <Plus
                size={16}
                strokeWidth={3}
                className={`rotate-${plusOrientation1} transition-all duration-300`}
              />
              Create new token
            </Button>
          </div>

          {/* Warning Message */}
          <div className="mb-6 p-4 bg-gray-800 rounded-lg border border-gray-700">
            <p className="text-gray-300 leading-relaxed">
              Access tokens authenticate your identity to Modaic and allow
              applications to perform actions based on token permissions.{" "}
              <span className="inline-flex items-center gap-1 font-semibold">
                <Info size={12} /> Do not share your Access Tokens with anyone;
              </span>{" "}
              we regularly check for leaked Access Tokens and remove them
              immediately.
            </p>
          </div>

          {/* Tokens Table - Using the new shadcn data table */}
          {tokens.length > 0 ? (
            <TokensTable tokens={tokens} />
          ) : (
            <div className="text-center py-12 mx-auto flex flex-col items-center text-gray-400">
              <Key
                size={28}
                strokeWidth={2}
                className="mb-4 text-muted-foreground"
              />
              <h3 className="text-lg font-medium mb-2 text-gray-300">
                No access tokens yet
              </h3>
              <p className="mb-4">
                Create your first access token to get started.
              </p>
              <Button
                onMouseEnter={() => setPlusOrientation2(45)}
                onMouseLeave={() => setPlusOrientation2(0)}
                className="px-4 py-2 rounded-md flex items-center gap-1 transition-colors"
              >
                <Plus
                  size={16}
                  strokeWidth={3}
                  className={`rotate-${plusOrientation2} transition-all duration-300`}
                />
                Create new token
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AccessTokensTab;
