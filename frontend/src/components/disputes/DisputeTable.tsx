/** Sortable, searchable, paginated dispute table. */
import { Link } from "react-router-dom";
import { ArrowUpDown, ChevronLeft, ChevronRight, Search } from "lucide-react";
import { useState } from "react";

import { StatusBadge } from "@/components/disputes/StatusBadge";
import { WinProbability } from "@/components/disputes/WinProbability";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDisputes } from "@/hooks/api";
import { formatDateTime, formatPaise } from "@/lib/format";
import { REASON_LABELS, STATUS_LABELS } from "@/services/mock/data";
import type { DisputeStatus, ReviewQueueParams } from "@/services/types";

type SortBy = NonNullable<ReviewQueueParams["sortBy"]>;

export function DisputeTable({
  title = "Review queue",
  description = "Chargebacks ranked by exposure and model confidence",
  pageSize = 8,
}: {
  title?: string;
  description?: string;
  pageSize?: number;
}) {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<DisputeStatus | "all">("all");
  const [sortBy, setSortBy] = useState<SortBy>("createdAt");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const { data, isLoading } = useDisputes({ page, pageSize, search, status, sortBy, sortDir });

  const toggleSort = (key: SortBy) => {
    if (sortBy === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortBy(key);
      setSortDir("desc");
    }
    setPage(1);
  };

  const total = data?.total ?? 0;
  const lastPage = Math.max(1, Math.ceil(total / pageSize));

  return (
    <Card className="glass">
      <CardHeader className="gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <CardTitle className="text-base">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search ID, merchant, email"
              className="w-full pl-9 sm:w-64"
            />
          </div>
          <Select
            value={status}
            onValueChange={(v) => {
              setStatus(v as DisputeStatus | "all");
              setPage(1);
            }}
          >
            <SelectTrigger className="w-full sm:w-44">
              <SelectValue placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              {Object.entries(STATUS_LABELS).map(([value, label]) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent>
        <div className="overflow-x-auto rounded-xl border border-border/70">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Dispute</TableHead>
                <TableHead className="hidden md:table-cell">Reason</TableHead>
                <TableHead>
                  <button
                    onClick={() => toggleSort("orderAmount")}
                    className="inline-flex items-center gap-1 hover:text-foreground"
                  >
                    Amount <ArrowUpDown className="size-3" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => toggleSort("winProbability")}
                    className="inline-flex items-center gap-1 hover:text-foreground"
                  >
                    Win prob. <ArrowUpDown className="size-3" />
                  </button>
                </TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="hidden lg:table-cell">
                  <button
                    onClick={() => toggleSort("createdAt")}
                    className="inline-flex items-center gap-1 hover:text-foreground"
                  >
                    Opened <ArrowUpDown className="size-3" />
                  </button>
                </TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}>
                      {Array.from({ length: 7 }).map((__, j) => (
                        <TableCell key={j}>
                          <Skeleton className="h-4 w-full" />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                : data?.items.map((d) => (
                    <TableRow key={d.id} className="transition-colors hover:bg-muted/40">
                      <TableCell>
                        <div className="font-medium">{d.id}</div>
                        <div className="text-xs text-muted-foreground">{d.merchantName}</div>
                      </TableCell>
                      <TableCell className="hidden text-sm text-muted-foreground md:table-cell">
                        {REASON_LABELS[d.reasonCode] ?? d.reasonCode}
                      </TableCell>
                      <TableCell className="font-medium tabular-nums">
                        {formatPaise(d.orderAmount)}
                      </TableCell>
                      <TableCell>
                        <WinProbability value={d.winProbability} />
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={d.status} />
                      </TableCell>
                      <TableCell className="hidden text-xs text-muted-foreground lg:table-cell">
                        {formatDateTime(d.createdAt)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button asChild size="sm" variant="ghost" className="interactive">
                          <Link to={`/disputes/${d.id}`}>
                            Open
                          </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
              {!isLoading && data?.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="py-10 text-center text-sm text-muted-foreground">
                    No disputes match those filters.
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>
        </div>

        <div className="mt-4 flex flex-col items-center justify-between gap-3 sm:flex-row">
          <p className="text-xs text-muted-foreground">
            Page {page} of {lastPage} · {total} disputes
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft className="size-4" /> Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= lastPage}
              onClick={() => setPage((p) => Math.min(lastPage, p + 1))}
            >
              Next <ChevronRight className="size-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
