import type { FoodCategory, DonorType, RecipientType } from "./types";

const numberFmt = new Intl.NumberFormat("en-US");

export function fmtInt(n: number): string {
  return numberFmt.format(Math.round(n));
}

export function fmtKg(n: number): string {
  return `${numberFmt.format(Math.round(n))} kg`;
}

export function fmtDelta(pct: number | null): { text: string; dir: "up" | "down" | "flat" } {
  if (pct === null || Number.isNaN(pct)) return { text: "—", dir: "flat" };
  const dir = pct > 0.05 ? "up" : pct < -0.05 ? "down" : "flat";
  const sign = pct > 0 ? "+" : "";
  return { text: `${sign}${pct.toFixed(1)}%`, dir };
}

const CATEGORY_LABELS: Record<FoodCategory, string> = {
  cooked: "Cooked meals",
  bakery: "Bakery",
  produce: "Produce",
  packaged: "Packaged",
};

const DONOR_TYPE_LABELS: Record<DonorType, string> = {
  restaurant: "Restaurant",
  canteen: "Canteen",
  hostel: "Hostel",
  event: "Event venue",
};

const RECIPIENT_TYPE_LABELS: Record<RecipientType, string> = {
  ngo: "NGO",
  shelter: "Shelter",
  community_kitchen: "Community kitchen",
};

export const categoryLabel = (c: FoodCategory) => CATEGORY_LABELS[c] ?? c;
export const donorTypeLabel = (t: DonorType) => DONOR_TYPE_LABELS[t] ?? t;
export const recipientTypeLabel = (t: RecipientType) => RECIPIENT_TYPE_LABELS[t] ?? t;

export function shortDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function timeOfDay(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
}

/** Live countdown text from an ISO expiry. Returns "Expired" past zero. */
export function countdownText(expiresIso: string, now: number = Date.now()): string {
  const diffMs = new Date(expiresIso).getTime() - now;
  if (diffMs <= 0) return "Expired";
  const totalMin = Math.floor(diffMs / 60000);
  const days = Math.floor(totalMin / (60 * 24));
  const hours = Math.floor((totalMin % (60 * 24)) / 60);
  const mins = totalMin % 60;
  const secs = Math.floor((diffMs % 60000) / 1000);
  if (days > 0) return `${days}d ${hours}h left`;
  if (hours > 0) return `${hours}h ${String(mins).padStart(2, "0")}m left`;
  return `${mins}m ${String(secs).padStart(2, "0")}s left`;
}
