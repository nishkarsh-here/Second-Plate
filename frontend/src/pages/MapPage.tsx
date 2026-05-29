import { useState } from "react";
import { useListings } from "@/lib/queries";
import { useAppState } from "@/state/appState";
import { RescueMap } from "@/components/map/RescueMap";
import { ClaimDialog } from "@/components/listings/ClaimDialog";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/common/ErrorState";
import type { Listing } from "@/lib/types";

const LEGEND = [
  { c: "#16A34A", l: "Fresh" },
  { c: "#F59E0B", l: "Expiring soon" },
  { c: "#E11D48", l: "Critical" },
];

export default function MapPage() {
  const { location } = useAppState();
  const [selected, setSelected] = useState<Listing | null>(null);
  const { data, isLoading, isError, error, refetch } = useListings({
    lat: location.lat,
    lng: location.lng,
    status: "available",
    limit: 200,
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-muted-foreground">{data?.length ?? 0} active rescues on the map</p>
        <div className="flex items-center gap-3">
          {LEGEND.map((x) => (
            <span key={x.l} className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span
                className="h-3 w-3 rounded-full border-2 border-white shadow"
                style={{ background: x.c }}
              />
              {x.l}
            </span>
          ))}
        </div>
      </div>

      {isError ? (
        <ErrorState error={error} onRetry={() => refetch()} />
      ) : (
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            {isLoading ? (
              <Skeleton className="h-[68vh] w-full" />
            ) : (
              <RescueMap
                listings={data ?? []}
                center={[location.lat, location.lng]}
                onClaim={setSelected}
              />
            )}
          </CardContent>
        </Card>
      )}

      <ClaimDialog listing={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
