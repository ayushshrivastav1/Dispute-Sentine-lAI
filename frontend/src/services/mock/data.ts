/**
 * Mock fixtures. All monetary values are integers in PAISE.
 * Shapes match src/services/types.ts exactly, so the real backend can drop in.
 */
import type {
  AnalyticsSummary,
  Dispute,
  DisputeDetail,
  DisputeStatus,
} from "@/services/types";

export const STATUS_LABELS: Record<DisputeStatus, string> = {
  escalated: "Escalated",
  auto_contested: "Auto-Contested",
  accepted_loss: "Accepted Loss",
  won: "Won",
  pending_evidence: "Pending Evidence",
};

export const REASON_LABELS: Record<string, string> = {
  chargeback_fraud: "chargeback_fraud",
  product_not_delivered: "product_not_delivered",
  product_not_as_described: "product_not_as_described",
  duplicate_charge: "duplicate_charge",
  subscription_canceled: "subscription_canceled",
};

export const disputes: Dispute[] = [
  {
    id: "disp_Ok98xYt2Rn41Qa",
    orderAmount: 4599900,
    currency: "INR",
    reasonCode: "chargeback_fraud",
    winProbability: 68,
    status: "escalated",
    merchantName: "Nimbus Electronics",
    customerEmail: "r.iyer@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-28T09:12:00.000Z",
    deadlineAt: "2026-09-06T09:12:00.000Z",
  },
  {
    id: "disp_Pq11zLm8Vt02Bd",
    orderAmount: 1289900,
    currency: "INR",
    reasonCode: "product_not_delivered",
    winProbability: 91,
    status: "auto_contested",
    merchantName: "Kettle & Co",
    customerEmail: "meera.n@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-27T16:40:00.000Z",
    deadlineAt: "2026-09-05T16:40:00.000Z",
  },
  {
    id: "disp_Zr74kDe1Xy55Cf",
    orderAmount: 899000,
    currency: "INR",
    reasonCode: "duplicate_charge",
    winProbability: 34,
    status: "accepted_loss",
    merchantName: "Trailhead Outfitters",
    customerEmail: "a.khan@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-26T11:05:00.000Z",
    deadlineAt: "2026-09-04T11:05:00.000Z",
  },
  {
    id: "disp_Hy32bCn9Kt18Lp",
    orderAmount: 21999900,
    currency: "INR",
    reasonCode: "chargeback_fraud",
    winProbability: 77,
    status: "escalated",
    merchantName: "Aurum Jewellers",
    customerEmail: "s.deshmukh@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-25T07:55:00.000Z",
    deadlineAt: "2026-09-03T07:55:00.000Z",
  },
  {
    id: "disp_Wq58mAe4Jr93Tn",
    orderAmount: 349900,
    currency: "INR",
    reasonCode: "product_not_as_described",
    winProbability: 52,
    status: "pending_evidence",
    merchantName: "Loom Living",
    customerEmail: "priya.b@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-25T13:21:00.000Z",
    deadlineAt: "2026-09-03T13:21:00.000Z",
  },
  {
    id: "disp_Cv90tRk6Nb27Uf",
    orderAmount: 7499900,
    currency: "INR",
    reasonCode: "subscription_canceled",
    winProbability: 88,
    status: "auto_contested",
    merchantName: "Peakform Fitness",
    customerEmail: "vikram.s@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-24T18:02:00.000Z",
    deadlineAt: "2026-09-02T18:02:00.000Z",
  },
  {
    id: "disp_Nf19sQu3Wp64Hk",
    orderAmount: 1599900,
    currency: "INR",
    reasonCode: "product_not_delivered",
    winProbability: 26,
    status: "escalated",
    merchantName: "Nimbus Electronics",
    customerEmail: "d.rao@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-24T10:44:00.000Z",
    deadlineAt: "2026-09-02T10:44:00.000Z",
  },
  {
    id: "disp_Bt45yGh7Dz80Mq",
    orderAmount: 5749900,
    currency: "INR",
    reasonCode: "chargeback_fraud",
    winProbability: 81,
    status: "won",
    merchantName: "Aurum Jewellers",
    customerEmail: "n.pillai@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-22T08:30:00.000Z",
    deadlineAt: "2026-08-31T08:30:00.000Z",
  },
  {
    id: "disp_Lm63pVc2Sx17Ay",
    orderAmount: 120000,
    currency: "INR",
    reasonCode: "duplicate_charge",
    winProbability: 95,
    status: "auto_contested",
    merchantName: "Kettle & Co",
    customerEmail: "t.george@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-21T15:10:00.000Z",
    deadlineAt: "2026-08-30T15:10:00.000Z",
  },
  {
    id: "disp_Ju27dFw5Er39Zi",
    orderAmount: 3299900,
    currency: "INR",
    reasonCode: "product_not_delivered",
    winProbability: 44,
    status: "pending_evidence",
    merchantName: "Trailhead Outfitters",
    customerEmail: "h.mehta@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-20T12:00:00.000Z",
    deadlineAt: "2026-08-29T12:00:00.000Z",
  },
  {
    id: "disp_Gx81nHl0Oy56Pv",
    orderAmount: 9899900,
    currency: "INR",
    reasonCode: "chargeback_fraud",
    winProbability: 72,
    status: "escalated",
    merchantName: "Peakform Fitness",
    customerEmail: "k.subramanian@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-19T09:47:00.000Z",
    deadlineAt: "2026-08-28T09:47:00.000Z",
  },
  {
    id: "disp_Ea36wTb8Ci72Rd",
    orderAmount: 649900,
    currency: "INR",
    reasonCode: "product_not_as_described",
    winProbability: 38,
    status: "accepted_loss",
    merchantName: "Loom Living",
    customerEmail: "s.banerjee@example.com",
    gateway: "razorpay",
    createdAt: "2026-08-18T17:25:00.000Z",
    deadlineAt: "2026-08-27T17:25:00.000Z",
  },
];

export const analyticsSummary: AnalyticsSummary = {
  totalContestedCapital: 145200000, // ₹14,52,000
  contestedCapitalChangePct: 12,
  winRate: 82.4,
  winRateTarget: 75,
  falsePositiveCost: 1240000, // ₹12,400
  falsePositiveCases: 6,
  activeEscalations: 14,
  trend: [
    { month: "Mar", contested: 82400000, recovered: 61300000 },
    { month: "Apr", contested: 96100000, recovered: 74800000 },
    { month: "May", contested: 88700000, recovered: 70100000 },
    { month: "Jun", contested: 114500000, recovered: 92600000 },
    { month: "Jul", contested: 129800000, recovered: 106400000 },
    { month: "Aug", contested: 145200000, recovered: 119600000 },
  ],
  statusBreakdown: [
    { status: "auto_contested", label: "Auto-Contested", count: 148 },
    { status: "escalated", label: "Escalated", count: 42 },
    { status: "won", label: "Won", count: 96 },
    { status: "accepted_loss", label: "Accepted Loss", count: 23 },
    { status: "pending_evidence", label: "Pending Evidence", count: 17 },
  ],
};

const detailById: Record<string, Partial<DisputeDetail>> = {
  disp_Ok98xYt2Rn41Qa: {
    evidence: {
      awbTrackingNumber: "DEL-8839201",
      courier: "Delhivery Express",
      ipAddress: "49.36.182.114",
      ipMatchesBillingCity: false,
      billingCity: "Mumbai, MH",
      ipCity: "Jaipur, RJ",
      signatureConfidence: 89,
      proofOfDeliveryUrl: null,
      timeline: [
        { label: "Picked up", location: "Bhiwandi Hub", at: "2026-08-20T06:10:00.000Z", completed: true },
        { label: "In transit", location: "Mumbai Sort Facility", at: "2026-08-21T02:35:00.000Z", completed: true },
        { label: "Out for delivery", location: "Andheri East", at: "2026-08-22T04:15:00.000Z", completed: true },
        { label: "Delivered — signature captured", location: "Andheri East", at: "2026-08-22T09:41:00.000Z", completed: true },
        { label: "Chargeback webhook received", location: "Razorpay", at: "2026-08-28T09:12:00.000Z", completed: true },
      ],
    },
    ai: {
      summary:
        "Courier confirms delivery with a captured signature at the billing address, and the OCR scan of the proof-of-delivery matches the cardholder name at 89% confidence. The order value, however, exceeds the auto-contest ceiling.",
      escalationReason:
        "Amount ₹45,999 exceeds auto-contest threshold of ₹25,000. Signature confidence is 89%.",
      autoContestThreshold: 2500000,
      contradiction: {
        severity: "high",
        headline: "Delivery confirmation contradicts cardholder location signal",
        detail:
          "The courier recorded an in-person signature in Mumbai (billing city) at 09:41 IST, while the checkout session IP geolocated to Jaipur, 1,150 km away, 4 minutes before dispatch confirmation. Either a household member accepted the parcel or the session was placed remotely.",
        conflictingSources: ["Delhivery POD signature", "Checkout session IP geolocation"],
      },
      attribution: [
        { label: "Signed proof of delivery (OCR 89%)", weight: 34, detail: "Cardholder surname matched on scanned receipt." },
        { label: "AWB scan chain complete", weight: 21, detail: "No gaps between pickup and delivery scans." },
        { label: "Device fingerprint reuse", weight: 15, detail: "Same device used for 6 prior undisputed orders." },
        { label: "Delivery address = billing address", weight: 12, detail: "Exact match, no last-minute edit." },
        { label: "IP geolocation mismatch", weight: -22, detail: "Session IP in Jaipur vs Mumbai billing city." },
        { label: "Filed 6 days after delivery", weight: -9, detail: "Late filing weakens non-receipt claims but invites friendly-fraud review." },
      ],
    },
    auditLedger: [
      { id: "log_1", event: "Webhook Received", actor: "razorpay.dispute.created", at: "2026-08-28T09:12:03.000Z", hash: "a91f4c07d2b8e5136f7c0a9e2b41d8c3f5e6a70b19c2d834ef5610ab7c92d4c02", verified: true },
      { id: "log_2", event: "Evidence Extracted", actor: "sentinel.evidence-agent", at: "2026-08-28T09:12:48.000Z", hash: "3d72be91af04c6152e8d7b30ca19f6428b5d0e73916cf24a8de5107b3c6f92aa", verified: true },
      { id: "log_3", event: "OCR Signature Scan", actor: "sentinel.ocr-worker", at: "2026-08-28T09:13:12.000Z", hash: "7f10ac48d93b2650e1c7fa82b40d69135ae2c8074f6b91d3ca580e26719bd3f4", verified: true },
      { id: "log_4", event: "Win Probability Scored", actor: "sentinel.scoring-v3", at: "2026-08-28T09:13:30.000Z", hash: "c58e2b71406fda93b8127ce5304a6f19d7b0e84c25913af6708db2c14e6905ab", verified: true },
      { id: "log_5", event: "Escalated to Human", actor: "sentinel.policy-engine", at: "2026-08-28T09:13:31.000Z", hash: "e2470bd15c93af8620d7e14b90cf35827a6b1049fe38c25d70914ba6c3f8d271", verified: true },
    ],
  },
};

const genericDetail = (dispute: Dispute): DisputeDetail => ({
  ...dispute,
  evidence: {
    awbTrackingNumber: `DEL-${dispute.id.slice(-7).replace(/\D/g, "3")}201`,
    courier: "Delhivery Express",
    ipAddress: "103.21.58.77",
    ipMatchesBillingCity: dispute.winProbability > 60,
    billingCity: "Bengaluru, KA",
    ipCity: dispute.winProbability > 60 ? "Bengaluru, KA" : "Kolkata, WB",
    signatureConfidence: Math.min(97, 45 + dispute.winProbability / 2),
    proofOfDeliveryUrl: null,
    timeline: [
      { label: "Picked up", location: "Origin Hub", at: dispute.createdAt, completed: true },
      { label: "In transit", location: "Regional Sort Facility", at: dispute.createdAt, completed: true },
      { label: "Out for delivery", location: "Local Facility", at: dispute.createdAt, completed: true },
      { label: "Delivered", location: "Customer Address", at: dispute.createdAt, completed: dispute.winProbability > 40 },
    ],
  },
  ai: {
    summary:
      "Automated evidence collection completed. Scoring engine weighed courier scans, device history and cardholder location signals.",
    escalationReason:
      dispute.status === "escalated"
        ? `Order value ${dispute.orderAmount / 100} exceeds auto-contest threshold or evidence confidence is below policy.`
        : "Case handled automatically by policy engine; no analyst action required.",
    autoContestThreshold: 2500000,
    contradiction:
      dispute.winProbability < 75
        ? {
            severity: dispute.winProbability < 40 ? "high" : "medium",
            headline: "Evidence sources disagree on delivery outcome",
            detail:
              "Courier scan chain reports a completed delivery while the cardholder's session signals and support transcript indicate non-receipt.",
            conflictingSources: ["Courier scan chain", "Support transcript"],
          }
        : null,
    attribution: [
      { label: "Courier scan chain", weight: 28, detail: "Delivery scan present and consistent." },
      { label: "Device fingerprint reuse", weight: 14, detail: "Recognised device from prior orders." },
      { label: "Address match", weight: 11, detail: "Billing and shipping addresses align." },
      { label: "Signature confidence", weight: dispute.winProbability > 60 ? 18 : -16, detail: "OCR confidence on proof of delivery." },
      { label: "Reason code base rate", weight: -12, detail: `Historical win rate for ${dispute.reasonCode}.` },
    ],
  },
  auditLedger: [
    { id: "log_1", event: "Webhook Received", actor: "razorpay.dispute.created", at: dispute.createdAt, hash: "b41c9e08d7a25f3610be47c92d8503fa16e7b204c95d38176af0e2b5c4d91367", verified: true },
    { id: "log_2", event: "Evidence Extracted", actor: "sentinel.evidence-agent", at: dispute.createdAt, hash: "5ea3170cb92f48d61307ac5be284f09d3b7160ea48c29d5f73b0164ae9c72d58", verified: true },
    { id: "log_3", event: "Win Probability Scored", actor: "sentinel.scoring-v3", at: dispute.createdAt, hash: "9c07f3a18b524de960137fc2ab5e408d72613ea0c94bd8f52076a3e1cb48d970", verified: true },
  ],
});

export function buildDisputeDetail(dispute: Dispute): DisputeDetail {
  const override = detailById[dispute.id];
  const base = genericDetail(dispute);
  return override ? ({ ...base, ...override } as DisputeDetail) : base;
}
