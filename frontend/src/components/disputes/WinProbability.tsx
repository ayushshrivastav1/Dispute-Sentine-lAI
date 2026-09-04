import { cn } from "@/lib/utils";
import { winProbabilityTone } from "@/lib/format";

const BAR: Record<string, string> = {
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-destructive",
};

const TEXT: Record<string, string> = {
  success: "text-success",
  warning: "text-warning",
  danger: "text-destructive",
};

export function WinProbability({ value, className }: { value: number; className?: string }) {
  const tone = winProbabilityTone(value);
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
        <div
          className={cn("h-full rounded-full transition-all", BAR[tone])}
          style={{ width: `${Math.max(2, Math.min(100, value))}%` }}
        />
      </div>
      <span className={cn("text-xs font-semibold tabular-nums", TEXT[tone])}>{value}%</span>
    </div>
  );
}
