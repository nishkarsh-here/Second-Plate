import { useState } from "react";
import { Soup } from "lucide-react";
import { useListings } from "@/lib/queries";
import { useAppState } from "@/state/appState";
import { ListingCard } from "@/components/listings/ListingCard";
import { ClaimDialog } from "@/components/listings/ClaimDialog";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { BrowseParams } from "@/lib/api";
import type { FoodCategory, Listing } from "@/lib/types";

const CATEGORIES = [
  { value: "all", label: "All categories" },
  { value: "cooked", label: "Cooked meals" },
  { value: "bakery", label: "Bakery" },
  { value: "produce", label: "Produce" },
  { value: "packaged", label: "Packaged" },
];

const RADII = [
  { value: "0", label: "Any distance" },
  { value: "5", label: "Within 5 km" },
  { value: "10", label: "Within 10 km" },
  { value: "25", label: "Within 25 km" },
];

function CardSkeleton() {
  return (
    <Card className="space-y-4 p-6">
      <div className="flex items-start justify-between">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
      <Skeleton className="h-9 w-28" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-40" />
        <Skeleton className="h-4 w-24" />
      </div>
      <Skeleton className="h-10 w-full rounded-lg" />
    </Card>
  );
}

export default function BrowseRescues() {
  const { location } = useAppState();
  const [category, setCategory] = useState("all");
  const [radius, setRadius] = useState("0");
  const [selected, setSelected] = useState<Listing | null>(null);

  const params: BrowseParams = {
    lat: location.lat,
    lng: location.lng,
    status: "available",
    limit: 120,
    ...(category !== "all" ? { category: category as FoodCategory } : {}),
    ...(radius !== "0" ? { radius: Number(radius) } : {}),
  };
  const { data, isLoading, isError, error, refetch } = useListings(params);
  const count = data?.length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-muted-foreground">
          {isLoading
            ? "Finding rescues near you…"
            : `${count} rescue${count === 1 ? "" : "s"} available nearby — most urgent first`}
        </p>
        <div className="flex items-center gap-2">
          <Select value={category} onValueChange={setCategory}>
            <SelectTrigger className="h-9 w-[160px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {CATEGORIES.map((c) => (
                <SelectItem key={c.value} value={c.value}>
                  {c.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={radius} onValueChange={setRadius}>
            <SelectTrigger className="h-9 w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {RADII.map((c) => (
                <SelectItem key={c.value} value={c.value}>
                  {c.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      )}

      {isError && <ErrorState error={error} onRetry={() => refetch()} />}

      {!isLoading &&
        !isError &&
        (count > 0 ? (
          <div className="grid animate-fade-in gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {data!.map((listing) => (
              <ListingCard key={listing.id} listing={listing} onClaim={setSelected} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Soup}
            title="No rescues right now"
            description="Nothing matches this filter yet. Try widening the distance or category — fresh listings show up here in real time."
          />
        ))}

      <ClaimDialog listing={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
