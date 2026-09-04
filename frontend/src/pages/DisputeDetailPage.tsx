import { useParams, Link } from "react-router-dom";
import { CheckCircle2, Circle, ShieldCheck, AlertTriangle, ChevronLeft, Loader2 } from "lucide-react";
import { useDispute, useDisputeAction } from "@/hooks/api";
import { formatPaise, formatDateTime, truncateHash, winProbabilityTone } from "@/lib/format";
import { StatusBadge } from "@/components/disputes/StatusBadge";
import { WinProbability } from "@/components/disputes/WinProbability";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { AttributionFactor } from "@/services/types";

function AttributionBar({ factor }: { factor: AttributionFactor }) {
  const isPositive = factor.weight >= 0;
  const width = `${Math.abs(factor.weight)}%`;
  return (
    <div className="flex items-center gap-3">
      <div className="w-40 truncate text-xs text-muted-foreground shrink-0" title={factor.label}>
        {factor.label}
      </div>
      <div className="flex-1 flex items-center gap-2">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
          <div
            className={cn("h-full rounded-full", isPositive ? "bg-success" : "bg-destructive")}
            style={{ width }}
          />
        </div>
        <span className={cn("text-xs font-semibold w-8 text-right tabular-nums", isPositive ? "text-success" : "text-destructive")}>
          {isPositive ? "+" : ""}{factor.weight}
        </span>
      </div>
    </div>
  );
}

export function DisputeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useDispute(id ?? "");
  const { mutate: doAction, isPending } = useDisputeAction(id ?? "");

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center gap-4 py-20">
        <ShieldCheck className="size-10 text-muted-foreground" />
        <p className="text-muted-foreground">Dispute not found.</p>
        <Link to="/queue"><Button variant="outline">Back to Queue</Button></Link>
      </div>
    );
  }

  const tone = winProbabilityTone(data.winProbability);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link to="/queue" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-2">
            <ChevronLeft className="size-3" /> Back to queue
          </Link>
          <h2 className="text-xl font-semibold tracking-tight">{data.id}</h2>
          <p className="text-sm text-muted-foreground">{data.merchantName} &middot; {data.customerEmail}</p>
        </div>
        <div className="flex items-center gap-3">
          <WinProbability value={data.winProbability} />
          <StatusBadge status={data.status} />
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {[
          { label: "Amount", value: formatPaise(data.orderAmount) },
          { label: "Reason", value: data.reasonCode.replace(/_/g, " ") },
          { label: "Opened", value: formatDateTime(data.createdAt) },
          { label: "Deadline", value: formatDateTime(data.deadlineAt) },
        ].map(item => (
          <div key={item.label} className="glass rounded-xl p-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">{item.label}</p>
            <p className="mt-1 text-sm font-semibold">{item.value}</p>
          </div>
        ))}
      </div>

      {/* AI Summary + Contradiction */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <ShieldCheck className="size-4 text-primary" /> AI Assessment
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">{data.ai.summary}</p>
          {data.ai.contradiction && (
            <div className={cn(
              "rounded-lg border p-4",
              data.ai.contradiction.severity === "high"
                ? "border-destructive/30 bg-destructive/10"
                : data.ai.contradiction.severity === "medium"
                  ? "border-warning/30 bg-warning/10"
                  : "border-border bg-muted/40"
            )}>
              <div className="flex items-start gap-2">
                <AlertTriangle className={cn(
                  "size-4 mt-0.5 shrink-0",
                  data.ai.contradiction.severity === "high" ? "text-destructive" : "text-warning"
                )} />
                <div>
                  <p className="text-sm font-semibold">{data.ai.contradiction.headline}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{data.ai.contradiction.detail}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {data.ai.contradiction.conflictingSources.map(src => (
                      <Badge key={src} variant="outline" className="text-xs">{src}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Evidence Timeline */}
        <Card className="glass">
          <CardHeader>
            <CardTitle className="text-base">Delivery Timeline</CardTitle>
            <CardDescription>AWB: {data.evidence.awbTrackingNumber} &middot; {data.evidence.courier}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative border-l-2 border-border ml-3 space-y-5">
              {data.evidence.timeline.map((event, idx) => (
                <div key={idx} className="relative pl-5">
                  <span className={cn(
                    "absolute -left-[9px] top-0.5 flex size-4 items-center justify-center rounded-full",
                    event.completed ? "bg-success text-success-foreground" : "bg-muted text-muted-foreground"
                  )}>
                    {event.completed
                      ? <CheckCircle2 className="size-3" />
                      : <Circle className="size-3" />
                    }
                  </span>
                  <p className="text-sm font-medium">{event.label}</p>
                  <p className="text-xs text-muted-foreground">{event.location} &middot; {formatDateTime(event.at)}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Attribution Factors */}
        <Card className="glass">
          <CardHeader>
            <CardTitle className="text-base">Win Probability Factors</CardTitle>
            <CardDescription>
              Score: <span className={cn("font-bold", tone === "success" ? "text-success" : tone === "warning" ? "text-warning" : "text-destructive")}>
                {data.winProbability}%
              </span>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.ai.attribution.map((factor, idx) => (
              <AttributionBar key={idx} factor={factor} />
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Audit Ledger */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="text-base">Cryptographic Audit Ledger</CardTitle>
          <CardDescription>Immutable SHA-256 hash chain</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative border-l-2 border-border ml-3 space-y-4">
            {data.auditLedger.map((entry) => (
              <div key={entry.id} className="relative pl-5">
                <span className="absolute -left-[9px] top-0.5 flex size-4 items-center justify-center rounded-full bg-primary/20">
                  <CheckCircle2 className="size-3 text-primary" />
                </span>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium">{entry.event}</p>
                    <p className="text-xs text-muted-foreground">{entry.actor} &middot; {formatDateTime(entry.at)}</p>
                  </div>
                  <Badge variant="outline" className="font-mono text-[10px] border-success/40 bg-success/10 text-success">
                    ✓ {truncateHash(entry.hash)}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      {(data.status === "escalated" || data.status === "pending_evidence") && (
        <div className="flex gap-3">
          <Button
            onClick={() => doAction("contest")}
            disabled={isPending}
            className="bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {isPending ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
            Contest Dispute
          </Button>
          <Button
            variant="outline"
            onClick={() => doAction("accept-loss")}
            disabled={isPending}
          >
            Accept Loss
          </Button>
        </div>
      )}
    </div>
  );
}
