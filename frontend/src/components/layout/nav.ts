import { BarChart3, ClipboardList, Map, Search, Sparkles, type LucideIcon } from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  end?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { to: "/browse", label: "Browse Rescues", icon: Search },
  { to: "/map", label: "Map", icon: Map },
  { to: "/impact", label: "Impact", icon: BarChart3 },
  { to: "/predictions", label: "Predictions", icon: Sparkles },
  { to: "/my-listings", label: "My Listings", icon: ClipboardList },
];

export const PAGE_TITLES: Record<string, string> = {
  "/browse": "Browse Rescues",
  "/map": "Rescue Map",
  "/impact": "Impact Dashboard",
  "/predictions": "Surplus Predictions",
  "/my-listings": "My Listings",
};
