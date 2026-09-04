import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { STATUS_LABELS } from "@/services/mock/data";
import type { DisputeStatus } from "@/services/types";

const TONE: Record<DisputeStatus, string> = {
  escalated: "border-warning/40 bg-warning/15 text-warning",
  auto_contested: "border-primary/40 bg-primary/15 text-primary",
  accepted_loss: "border-destructive/40 bg-destructive/15 text-destructive",
  won: "border-success/40 bg-success/15 text-success",
  pending_evidence: "border-border bg-muted/60 text-muted-foreground",
};

export function StatusBadge({ status }: { status: DisputeStatus }) {
  return (
    <Badge variant="outline" className={cn("font-medium", TONE[status])}>
      {STATUS_LABELS[status]}
    </Badge>
  );
}
