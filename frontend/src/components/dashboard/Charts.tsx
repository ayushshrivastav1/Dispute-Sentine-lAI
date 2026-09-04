/** Recharts visuals for the analytics summary. */
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatPaiseCompact } from "@/lib/format";
import type { AnalyticsSummary } from "@/services/types";

const axis = {
  stroke: "var(--muted-foreground)",
  fontSize: 11,
  tickLine: false,
  axisLine: false,
};

function ChartTooltip({ active, payload, label, money }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="mb-1 font-medium text-foreground">{label}</p>
      {payload.map((entry: any) => (
        <p key={entry.dataKey} className="flex items-center gap-2 text-muted-foreground">
          <span
            className="inline-block size-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          {entry.name}:{" "}
          <span className="font-medium text-foreground">
            {money ? formatPaiseCompact(entry.value as number) : entry.value}
          </span>
        </p>
      ))}
    </div>
  );
}

export function RecoveryTrendChart({ data, loading }: { data?: AnalyticsSummary; loading: boolean }) {
  return (
    <Card className="glass">
      <CardHeader>
        <CardTitle className="text-base">Contested vs recovered capital</CardTitle>
        <CardDescription>Rolling 8 months, gross dispute value</CardDescription>
      </CardHeader>
      <CardContent className="h-[280px]">
        {loading || !data ? (
          <Skeleton className="size-full" />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.trend} margin={{ left: 4, right: 8, top: 8 }}>
              <defs>
                <linearGradient id="gContested" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gRecovered" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--chart-2)" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="var(--chart-2)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="month" {...axis} />
              <YAxis {...axis} tickFormatter={(v) => formatPaiseCompact(Number(v))} width={72} />
              <Tooltip content={<ChartTooltip money />} cursor={{ stroke: "var(--border)" }} />
              <Area
                type="monotone"
                dataKey="contested"
                name="Contested"
                stroke="var(--chart-1)"
                fill="url(#gContested)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="recovered"
                name="Recovered"
                stroke="var(--chart-2)"
                fill="url(#gRecovered)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

const STATUS_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

export function StatusBreakdownChart({
  data,
  loading,
}: {
  data?: AnalyticsSummary;
  loading: boolean;
}) {
  return (
    <Card className="glass">
      <CardHeader>
        <CardTitle className="text-base">Disposition mix</CardTitle>
        <CardDescription>How the engine resolved open chargebacks</CardDescription>
      </CardHeader>
      <CardContent className="h-[280px]">
        {loading || !data ? (
          <Skeleton className="size-full" />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.statusBreakdown} margin={{ left: 4, right: 8, top: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="label" {...axis} interval={0} tick={{ fontSize: 10 }} />
              <YAxis {...axis} width={32} allowDecimals={false} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--muted)", opacity: 0.3 }} />
              <Bar dataKey="count" name="Disputes" radius={[6, 6, 0, 0]}>
                {data.statusBreakdown.map((entry, i) => (
                  <Cell key={entry.status} fill={STATUS_COLORS[i % STATUS_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
