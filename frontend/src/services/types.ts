/**
 * API contracts shared by the mock adapter and the real backend.
 * Swap `VITE_USE_MOCK_API=false` and these same types must hold.
 */

export type DisputeStatus =
  | "escalated"
  | "auto_contested"
  | "accepted_loss"
  | "won"
  | "pending_evidence";

export type ReasonCode =
  | "chargeback_fraud"
  | "product_not_delivered"
  | "product_not_as_described"
  | "duplicate_charge"
  | "subscription_canceled";

export interface Dispute {
  id: string;
  /** Integer PAISE. 4599900 === ₹45,999.00 */
  orderAmount: number;
  currency: "INR";
  reasonCode: ReasonCode;
  /** 0-100 */
  winProbability: number;
  status: DisputeStatus;
  merchantName: string;
  customerEmail: string;
  gateway: "razorpay";
  createdAt: string;
  deadlineAt: string;
}

export interface EvidenceTimelineEntry {
  label: string;
  location: string;
  at: string;
  completed: boolean;
}

export interface AttributionFactor {
  label: string;
  /** Signed weight, -100..100. Positive supports contesting. */
  weight: number;
  detail: string;
}

export interface SemanticContradiction {
  severity: "high" | "medium" | "low";
  headline: string;
  detail: string;
  conflictingSources: [string, string];
}

export interface AuditLogEntry {
  id: string;
  event: string;
  actor: string;
  at: string;
  /** SHA-256 hex digest of the ledger entry. */
  hash: string;
  verified: boolean;
}

export interface DisputeDetail extends Dispute {
  evidence: {
    awbTrackingNumber: string;
    courier: string;
    ipAddress: string;
    ipMatchesBillingCity: boolean;
    billingCity: string;
    ipCity: string;
    signatureConfidence: number;
    proofOfDeliveryUrl: string | null;
    timeline: EvidenceTimelineEntry[];
  };
  ai: {
    summary: string;
    escalationReason: string;
    autoContestThreshold: number;
    contradiction: SemanticContradiction | null;
    attribution: AttributionFactor[];
  };
  auditLedger: AuditLogEntry[];
}

export interface AnalyticsSummary {
  /** Integer PAISE */
  totalContestedCapital: number;
  contestedCapitalChangePct: number;
  winRate: number;
  winRateTarget: number;
  /** Integer PAISE lost to bad auto-contests */
  falsePositiveCost: number;
  falsePositiveCases: number;
  activeEscalations: number;
  trend: Array<{
    month: string;
    /** PAISE */
    contested: number;
    /** PAISE */
    recovered: number;
  }>;
  statusBreakdown: Array<{ status: DisputeStatus; label: string; count: number }>;
}

export interface Paginated<T> {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
}

export interface ReviewQueueParams {
  page?: number;
  pageSize?: number;
  sortBy?: "orderAmount" | "winProbability" | "createdAt";
  sortDir?: "asc" | "desc";
  search?: string;
  status?: DisputeStatus | "all";
}

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: "risk_analyst" | "admin";
  organization: string;
}

export interface AuthSession {
  token: string;
  user: AuthUser;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface SignupPayload {
  name: string;
  organization: string;
  email: string;
  password: string;
}
