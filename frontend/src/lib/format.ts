/**
 * Formatting helpers.
 *
 * IMPORTANT: every monetary value crossing the API boundary is an integer in
 * PAISE (1/100 of a rupee). `amount: 120000` means ₹1,200.00. Never divide by
 * 100 inline in a component — always go through these helpers so switching
 * VITE_USE_MOCK_API=false cannot introduce conversion bugs.
 */

const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 2,
});

const inrCompact = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

/** 120000 (paise) -> "₹1,200.00" */
export function formatPaise(amountInPaise: number): string {
  return inr.format(amountInPaise / 100);
}

/** 145200000 (paise) -> "₹14,52,000" */
export function formatPaiseCompact(amountInPaise: number): string {
  return inrCompact.format(Math.round(amountInPaise / 100));
}

/** 82.4 -> "82.4%" */
export function formatPercent(value: number, fractionDigits = 1): string {
  return `${value.toFixed(fractionDigits)}%`;
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Truncate a long hash for badge display: "a91f…4c02" */
export function truncateHash(hash: string, edge = 6): string {
  if (hash.length <= edge * 2 + 1) return hash;
  return `${hash.slice(0, edge)}…${hash.slice(-4)}`;
}

export type RiskTone = "danger" | "warning" | "success";

/** Win-probability colour bands: red <40, amber 40-74, green >=75. */
export function winProbabilityTone(probability: number): RiskTone {
  if (probability < 40) return "danger";
  if (probability < 75) return "warning";
  return "success";
}
