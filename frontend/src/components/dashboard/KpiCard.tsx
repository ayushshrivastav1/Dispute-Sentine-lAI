import { TrendingDown, TrendingUp, type LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export function KpiCard({
  label,
  value,
  hint,
  icon: Icon,
  changePct,
  loading,
}: {
  label: string;
  value: string;
  hint?: string;
  icon: LucideIcon;
  changePct?: number;
  loading?: boolean;
}) {
  const positive = (changePct ?? 0) >= 0;
  return (
    <Card className="glass interactive overflow-hidden">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {label}
          </p>
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/25">
            <Icon className="size-4" />
          </span>
        </div>
        {loading ? (
          <Skeleton className="mt-4 h-8 w-32" />
        ) : (
          <p className="mt-3 text-2xl font-semibold tracking-tight tabular-nums">{value}</p>
        )}
        <div className="mt-2 flex items-center gap-2">
          {changePct !== undefined && !loading ? (
            <span
              className={cn(
                "inline-flex items-center gap-1 text-xs font-medium",
                positive ? "text-success" : "text-destructive",
              )}
            >
              {positive ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}
              {Math.abs(changePct).toFixed(1)}%
            </span>
          ) : null}
          {hint ? <span className="text-xs text-muted-foreground">{hint}</span> : null}
        </div>
      </CardContent>
    </Card>
  );
}
