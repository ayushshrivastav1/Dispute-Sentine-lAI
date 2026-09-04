/**
 * Mock API adapter.
 *
 * Keyed by the SAME endpoint paths + response envelopes the real backend
 * exposes, so flipping VITE_USE_MOCK_API=false is a drop-in swap.
 */
import { ApiError } from "@/services/http";
import {
  analyticsSummary,
  buildDisputeDetail,
  disputes,
} from "@/services/mock/data";
import type {
  AuthSession,
  Dispute,
  DisputeStatus,
  LoginPayload,
  Paginated,
  SignupPayload,
} from "@/services/types";

const LATENCY_MS = 320;

const delay = (ms = LATENCY_MS) => new Promise((r) => setTimeout(r, ms));

function session(name: string, email: string, organization: string): AuthSession {
  return {
    token: `mock.${btoa(email)}.jwt`,
    user: {
      id: "usr_demo_1",
      name,
      email,
      role: "risk_analyst",
      organization,
    },
  };
}

function queryOf(fullPath: string) {
  const [path, qs] = fullPath.split("?");
  return { path: path ?? fullPath, params: new URLSearchParams(qs ?? "") };
}

function listDisputes(params: URLSearchParams): Paginated<Dispute> {
  const page = Number(params.get("page") ?? 1);
  const pageSize = Number(params.get("pageSize") ?? 10);
  const search = (params.get("search") ?? "").toLowerCase();
  const status = (params.get("status") ?? "all") as DisputeStatus | "all";
  const sortBy = params.get("sortBy") as keyof Dispute | null;
  const sortDir = params.get("sortDir") === "asc" ? 1 : -1;

  let items = disputes.filter((d) => {
    const matchesStatus = status === "all" || d.status === status;
    const matchesSearch =
      !search ||
      d.id.toLowerCase().includes(search) ||
      d.merchantName.toLowerCase().includes(search) ||
      d.customerEmail.toLowerCase().includes(search);
    return matchesStatus && matchesSearch;
  });

  if (sortBy) {
    items = [...items].sort((a, b) => {
      const av = a[sortBy];
      const bv = b[sortBy];
      if (typeof av === "number" && typeof bv === "number") return (av - bv) * sortDir;
      return String(av).localeCompare(String(bv)) * sortDir;
    });
  }

  const total = items.length;
  const start = (page - 1) * pageSize;
  return { items: items.slice(start, start + pageSize), page, pageSize, total };
}

export async function handleMockRequest(
  method: string,
  fullPath: string,
  body?: unknown,
): Promise<unknown> {
  await delay();
  const { path, params } = queryOf(fullPath);

  if (method === "POST" && path === "/api/v1/auth/login") {
    const payload = body as LoginPayload;
    if (!payload?.email || !payload?.password) {
      throw new ApiError("Email and password are required.", 400);
    }
    return session("Ananya Rao", payload.email, "Northwind Commerce");
  }

  if (method === "POST" && path === "/api/v1/auth/signup") {
    const payload = body as SignupPayload;
    return session(payload.name, payload.email, payload.organization);
  }

  if (method === "GET" && path === "/api/v1/analytics/summary") {
    return analyticsSummary;
  }

  if (method === "GET" && (path === "/api/v1/review-queue" || path === "/api/v1/disputes")) {
    return listDisputes(params);
  }

  const detailMatch = /^\/api\/v1\/disputes\/([^/]+)$/.exec(path);
  if (method === "GET" && detailMatch) {
    const dispute = disputes.find((d) => d.id === detailMatch[1]);
    if (!dispute) throw new ApiError("Dispute not found.", 404);
    return buildDisputeDetail(dispute);
  }

  const actionMatch = /^\/api\/v1\/disputes\/([^/]+)\/(contest|accept-loss)$/.exec(path);
  if (method === "POST" && actionMatch) {
    const dispute = disputes.find((d) => d.id === actionMatch[1]);
    if (!dispute) throw new ApiError("Dispute not found.", 404);
    dispute.status = actionMatch[2] === "contest" ? "auto_contested" : "accepted_loss";
    return buildDisputeDetail(dispute);
  }

  throw new ApiError(`No mock handler for ${method} ${path}`, 404);
}
