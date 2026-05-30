import axios from "axios";
import type {
  AuthResponse,
  AuthUser,
  Donor,
  Health,
  ImpactSummary,
  Listing,
  ListingCreate,
  ListingStatus,
  FoodCategory,
  Pickup,
  PredictionExplain,
  Recipient,
  RegisterPayload,
  RetrainMetrics,
  SurplusPrediction,
  TrendsResponse,
} from "./types";

// Empty base in dev -> Vite proxies /api and /health to the backend.
const client = axios.create({ baseURL: import.meta.env.VITE_API_BASE || "" });

// Attach the bearer token (if present) to every request.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("sp-token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export interface BrowseParams {
  lat?: number;
  lng?: number;
  radius?: number;
  status?: ListingStatus;
  category?: FoodCategory;
  limit?: number;
}

export const Api = {
  health: () => client.get<Health>("/health").then((r) => r.data),
  donors: () => client.get<Donor[]>("/api/donors").then((r) => r.data),
  recipients: () => client.get<Recipient[]>("/api/recipients").then((r) => r.data),
  browse: (params: BrowseParams) =>
    client.get<Listing[]>("/api/listings", { params }).then((r) => r.data),
  listing: (id: number) => client.get<Listing>(`/api/listings/${id}`).then((r) => r.data),
  donorListings: (donorId: number) =>
    client.get<Listing[]>(`/api/listings/donor/${donorId}`).then((r) => r.data),
  createListing: (body: ListingCreate) =>
    client.post<Listing>("/api/listings", body).then((r) => r.data),
  claim: (id: number, body: { recipient_id: number; scheduled_at?: string }) =>
    client.post<Pickup>(`/api/listings/${id}/claim`, body).then((r) => r.data),
  impactSummary: (windowDays = 30) =>
    client
      .get<ImpactSummary>("/api/impact/summary", { params: { window_days: windowDays } })
      .then((r) => r.data),
  impactTrends: (rangeDays = 30) =>
    client
      .get<TrendsResponse>("/api/impact/trends", { params: { range: rangeDays } })
      .then((r) => r.data),
  predictions: () =>
    client.get<SurplusPrediction[]>("/api/predictions/surplus").then((r) => r.data),
  explain: (donorId: number) =>
    client.get<PredictionExplain>(`/api/predictions/${donorId}/explain`).then((r) => r.data),
  retrain: () => client.post<RetrainMetrics>("/api/ml/retrain").then((r) => r.data),
  auth: {
    register: (body: RegisterPayload) =>
      client.post<AuthResponse>("/api/auth/register", body).then((r) => r.data),
    login: (body: { email: string; password: string }) =>
      client.post<AuthResponse>("/api/auth/login", body).then((r) => r.data),
    me: () => client.get<AuthUser>("/api/auth/me").then((r) => r.data),
  },
};

export function apiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length) return detail[0]?.msg ?? "Validation error";
    return err.message;
  }
  return "Something went wrong";
}
