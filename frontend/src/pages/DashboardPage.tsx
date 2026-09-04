import { ShieldCheck, Target, TrendingUp, AlertTriangle } from "lucide-react";
import { useAnalyticsSummary } from "@/hooks/api";
import { formatPaiseCompact } from "@/lib/format";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { RecoveryTrendChart, StatusBreakdownChart } from "@/components/dashboard/Charts";

export function DashboardPage() {
  const { data, isLoading } = useAnalyticsSummary();

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Contested Capital"
          value={data ? formatPaiseCompact(data.totalContestedCapital) : "—"}
          changePct={data?.contestedCapitalChangePct}
          icon={TrendingUp}
          loading={isLoading}
        />
        <KpiCard
          label="Win Rate"
          value={data ? `${data.winRate}%` : "—"}
          hint={`Target: ${data?.winRateTarget}%`}
          changePct={data ? data.winRate - data.winRateTarget : 0}
          icon={Target}
          loading={isLoading}
        />
        <KpiCard
          label="Active Escalations"
          value={data ? String(data.activeEscalations) : "—"}
          hint="Needs manual review"
          icon={ShieldCheck}
          loading={isLoading}
        />
        <KpiCard
          label="False Positive Cost"
          value={data ? formatPaiseCompact(data.falsePositiveCost) : "—"}
          hint={`${data?.falsePositiveCases} cases reversed`}
          icon={AlertTriangle}
          loading={isLoading}
        />
      </div>
      <div className="grid gap-4 md:grid-cols-7">
        <div className="col-span-4">
          <RecoveryTrendChart data={data} loading={isLoading} />
        </div>
        <div className="col-span-3">
          <StatusBreakdownChart data={data} loading={isLoading} />
        </div>
      </div>
    </div>
  );
}
