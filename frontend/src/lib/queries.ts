import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Api, type BrowseParams } from "./api";
import type { ListingCreate } from "./types";

export const keys = {
  health: ["health"] as const,
  donors: ["donors"] as const,
  recipients: ["recipients"] as const,
  listings: (p: BrowseParams) => ["listings", p] as const,
  donorListings: (id: number) => ["donorListings", id] as const,
  impactSummary: (w: number) => ["impactSummary", w] as const,
  impactTrends: (r: number) => ["impactTrends", r] as const,
  predictions: ["predictions"] as const,
  explain: (id: number) => ["explain", id] as const,
};

export const useHealth = () => useQuery({ queryKey: keys.health, queryFn: Api.health });
export const useDonors = () => useQuery({ queryKey: keys.donors, queryFn: Api.donors });
export const useRecipients = () =>
  useQuery({ queryKey: keys.recipients, queryFn: Api.recipients });

export const useListings = (params: BrowseParams) =>
  useQuery({ queryKey: keys.listings(params), queryFn: () => Api.browse(params) });

export const useDonorListings = (donorId: number | null) =>
  useQuery({
    queryKey: keys.donorListings(donorId ?? 0),
    queryFn: () => Api.donorListings(donorId as number),
    enabled: donorId != null,
  });

export const useImpactSummary = (windowDays = 30) =>
  useQuery({ queryKey: keys.impactSummary(windowDays), queryFn: () => Api.impactSummary(windowDays) });

export const useImpactTrends = (rangeDays = 30) =>
  useQuery({ queryKey: keys.impactTrends(rangeDays), queryFn: () => Api.impactTrends(rangeDays) });

export const usePredictions = () =>
  useQuery({ queryKey: keys.predictions, queryFn: Api.predictions });

export const useExplain = (donorId: number | null) =>
  useQuery({
    queryKey: keys.explain(donorId ?? 0),
    queryFn: () => Api.explain(donorId as number),
    enabled: donorId != null,
  });

export function useCreateListing() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: ListingCreate) => Api.createListing(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["listings"] });
      qc.invalidateQueries({ queryKey: ["donorListings"] });
    },
  });
}

export function useClaimListing() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, recipientId }: { id: number; recipientId: number }) =>
      Api.claim(id, { recipient_id: recipientId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["listings"] });
      qc.invalidateQueries({ queryKey: ["donorListings"] });
      qc.invalidateQueries({ queryKey: ["impactSummary"] });
    },
  });
}

export function useRetrain() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => Api.retrain(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["predictions"] });
      qc.invalidateQueries({ queryKey: ["health"] });
    },
  });
}
