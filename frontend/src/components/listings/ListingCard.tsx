import { MapPin, Store, Utensils } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FreshnessBadge } from "./FreshnessBadge";
import { categoryLabel, donorTypeLabel, fmtInt } from "@/lib/format";
import type { Listing } from "@/lib/types";

export function ListingCard({
  listing,
  onClaim,
}: {
  listing: Listing;
  onClaim?: (listing: Listing) => void;
}) {
  const canClaim = listing.status === "available";

  return (
    <Card className="group flex flex-col p-6 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lift">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <Badge variant="muted" className="mb-2">
            {categoryLabel(listing.category)}
          </Badge>
          <h3 className="truncate text-base font-semibold" title={listing.food_type}>
            {listing.food_type}
          </h3>
        </div>
        <FreshnessBadge urgency={listing.urgency} expiresAt={listing.expires_at} />
      </div>

      <div className="mt-4 flex items-end gap-2">
        <span className="text-3xl font-bold tabular-nums leading-none">{fmtInt(listing.servings)}</span>
        <span className="pb-0.5 text-sm text-muted-foreground">servings</span>
        <Utensils className="ml-auto h-5 w-5 text-primary/70" />
      </div>

      <div className="mt-4 space-y-1.5 text-sm">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Store className="h-4 w-4 shrink-0" />
          <span className="truncate text-foreground">{listing.donor.name}</span>
          <span className="shrink-0 text-xs">· {donorTypeLabel(listing.donor.type)}</span>
        </div>
        {listing.distance_km != null && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <MapPin className="h-4 w-4 shrink-0" />
            <span>{listing.distance_km} km away</span>
          </div>
        )}
      </div>

      <div className="mt-5 flex items-center">
        {canClaim ? (
          <Button className="w-full" onClick={() => onClaim?.(listing)}>
            Claim pickup
          </Button>
        ) : (
          <Badge variant="secondary" className="capitalize">
            {listing.status.replace("_", " ")}
          </Badge>
        )}
      </div>
    </Card>
  );
}
