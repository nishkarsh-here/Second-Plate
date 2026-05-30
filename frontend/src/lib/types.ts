// Mirrors the backend Pydantic schemas.

export type DonorType = "restaurant" | "canteen" | "hostel" | "event";
export type RecipientType = "ngo" | "shelter" | "community_kitchen";
export type FoodCategory = "cooked" | "bakery" | "produce" | "packaged";
export type ListingStatus = "available" | "claimed" | "picked_up" | "expired";
export type UrgencyColor = "green" | "amber" | "rose" | "slate";

export interface DonorBrief {
  id: number;
  name: string;
  type: DonorType;
}

export interface Donor extends DonorBrief {
  lat: number;
  lng: number;
  address: string;
  created_at: string;
}

export interface RecipientBrief {
  id: number;
  name: string;
  type: RecipientType;
}

export interface Recipient extends RecipientBrief {
  lat: number;
  lng: number;
  capacity: number;
  created_at: string;
}

export interface UrgencyInfo {
  score: number;
  level: "fresh" | "soon" | "critical" | "expired";
  color: UrgencyColor;
  minutes_to_expiry: number;
  label: string;
}

export interface Listing {
  id: number;
  food_type: string;
  category: FoodCategory;
  servings: number;
  prepared_at: string;
  expires_at: string;
  status: ListingStatus;
  lat: number;
  lng: number;
  created_at: string;
  donor: DonorBrief;
  urgency: UrgencyInfo;
  distance_km: number | null;
}

export interface ListingCreate {
  donor_id: number;
  food_type: string;
  category: FoodCategory;
  servings: number;
  prepared_at: string;
  expires_at: string;
  lat?: number | null;
  lng?: number | null;
}

export interface Pickup {
  id: number;
  listing_id: number;
  recipient_id: number;
  scheduled_at: string;
  completed_at: string | null;
  servings_rescued: number;
  recipient: RecipientBrief | null;
}

export interface StatDelta {
  value: number;
  delta_pct: number | null;
}

export interface ImpactSummary {
  meals_rescued: StatDelta;
  kg_saved: StatDelta;
  co2e_avoided_kg: StatDelta;
  people_served: StatDelta;
  active_listings: number;
  total_donors: number;
  total_recipients: number;
  window_days: number;
}

export interface TrendPoint {
  date: string;
  meals: number;
  kg_saved: number;
}

export interface CategoryBreakdown {
  category: FoodCategory;
  servings: number;
  kg_saved: number;
}

export interface TopDonor {
  donor_id: number;
  name: string;
  type: string;
  meals: number;
  rescues: number;
}

export interface TrendsResponse {
  range_days: number;
  series: TrendPoint[];
  by_category: CategoryBreakdown[];
  top_donors: TopDonor[];
}

export interface FactorContribution {
  feature: string;
  label: string;
  value: number;
  contribution: number;
  importance: number;
}

export interface SurplusPrediction {
  donor_id: number;
  donor_name: string;
  donor_type: DonorType;
  predicted_servings: number;
  confidence: number;
  recent_avg_servings: number;
  top_factors: FactorContribution[];
}

export interface PredictionExplain {
  donor_id: number;
  donor_name: string;
  predicted_servings: number;
  confidence: number;
  factors: FactorContribution[];
  model_version: string;
  trained_at: string | null;
}

export interface RetrainMetrics {
  mae: number;
  rmse: number;
  r2: number;
  n_train: number;
  n_test: number;
  n_features: number;
  feature_importances: Record<string, number>;
  trained_at: string;
  model_version: string;
}

export interface Health {
  status: string;
  app: string;
  environment: string;
  database: string;
  model_loaded: boolean;
}

export type AuthRole = "donor" | "recipient";

export interface AuthUser {
  id: number;
  email: string;
  role: AuthRole;
  name: string;
  lat: number | null;
  lng: number | null;
  donor_id: number | null;
  recipient_id: number | null;
}

export interface RegisterPayload {
  email: string;
  password: string;
  name: string;
  role: AuthRole;
  donor_type?: DonorType;
  recipient_type?: RecipientType;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}
