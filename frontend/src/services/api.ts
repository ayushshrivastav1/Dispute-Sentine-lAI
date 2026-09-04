/**
 * API service layer.
 *
 * The ONLY place endpoint paths live. Components never call fetch directly —
 * they go through the hooks in src/hooks/api.ts which call these functions.
 * Swap the backend by setting VITE_API_BASE_URL + VITE_USE_MOCK_API=false.
 */
import { request } from "@/services/http";
import type {
  AnalyticsSummary,
  AuthSession,
  Dispute,
  DisputeDetail,
  LoginPayload,
  Paginated,
  ReviewQueueParams,
  SignupPayload,
} from "@/services/types";

export const endpoints = {
  login: "/api/v1/auth/login",
  signup: "/api/v1/auth/signup",
  disputes: "/api/v1/disputes",
  reviewQueue: "/api/v1/review-queue",
  analyticsSummary: "/api/v1/analytics/summary",
  dispute: (id: string) => `/api/v1/disputes/${id}`,
  contest: (id: string) => `/api/v1/disputes/${id}/contest`,
  acceptLoss: (id: string) => `/api/v1/disputes/${id}/accept-loss`,
} as const;

export const authApi = {
  login: (payload: LoginPayload) =>
    request<AuthSession>(endpoints.login, {
      method: "POST",
      body: payload,
      auth: false,
    }),
  signup: (payload: SignupPayload) =>
    request<AuthSession>(endpoints.signup, {
      method: "POST",
      body: payload,
      auth: false,
    }),
};

export const analyticsApi = {
  summary: () => request<AnalyticsSummary>(endpoints.analyticsSummary),
};

function queueQuery(params: ReviewQueueParams) {
  return {
    page: params.page,
    pageSize: params.pageSize,
    sortBy: params.sortBy,
    sortDir: params.sortDir,
    search: params.search,
    status: params.status === "all" ? undefined : params.status,
  };
}

export const disputesApi = {
  list: (params: ReviewQueueParams = {}) =>
    request<Paginated<Dispute>>(endpoints.disputes, { query: queueQuery(params) }),
  reviewQueue: (params: ReviewQueueParams = {}) =>
    request<Paginated<Dispute>>(endpoints.reviewQueue, { query: queueQuery(params) }),
  detail: (id: string) => request<DisputeDetail>(endpoints.dispute(id)),
  contest: (id: string) => request<DisputeDetail>(endpoints.contest(id), { method: "POST" }),
  acceptLoss: (id: string) => request<DisputeDetail>(endpoints.acceptLoss(id), { method: "POST" }),
};
