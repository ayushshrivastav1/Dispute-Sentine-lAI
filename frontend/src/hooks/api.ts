/**
 * TanStack Query hooks wrapping the API service layer.
 * Components consume these only — never the raw client.
 */
import { useMutation, useQuery, useQueryClient, queryOptions } from "@tanstack/react-query";

import { analyticsApi, disputesApi } from "@/services/api";
import type { ReviewQueueParams } from "@/services/types";

export const queryKeys = {
  analytics: ["analytics", "summary"] as const,
  disputes: (params: ReviewQueueParams) => ["disputes", params] as const,
  dispute: (id: string) => ["disputes", id] as const,
};

export const analyticsQueryOptions = () =>
  queryOptions({
    queryKey: queryKeys.analytics,
    queryFn: () => analyticsApi.summary(),
  });

export function useAnalyticsSummary() {
  return useQuery(analyticsQueryOptions());
}

export function useDisputes(params: ReviewQueueParams) {
  return useQuery({
    queryKey: queryKeys.disputes(params),
    queryFn: () => disputesApi.reviewQueue(params),
    placeholderData: (prev) => prev,
  });
}

export function useDispute(id: string) {
  return useQuery({
    queryKey: queryKeys.dispute(id),
    queryFn: () => disputesApi.detail(id),
    enabled: Boolean(id),
  });
}

export function useDisputeAction(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (action: "contest" | "accept-loss") =>
      action === "contest" ? disputesApi.contest(id) : disputesApi.acceptLoss(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.dispute(id) });
      queryClient.invalidateQueries({ queryKey: ["disputes"] });
      queryClient.invalidateQueries({ queryKey: queryKeys.analytics });
    },
  });
}
