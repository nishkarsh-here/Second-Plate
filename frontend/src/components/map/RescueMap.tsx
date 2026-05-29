import { useEffect } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import { Button } from "@/components/ui/button";
import { categoryLabel, donorTypeLabel, fmtInt } from "@/lib/format";
import type { Listing } from "@/lib/types";

const PIN_COLORS: Record<string, string> = {
  green: "#16A34A",
  amber: "#F59E0B",
  rose: "#E11D48",
  slate: "#64748B",
};

function pinIcon(color: string) {
  return L.divIcon({
    className: "",
    html: `<span style="display:block;width:18px;height:18px;border-radius:9999px;background:${color};border:3px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.4)"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    popupAnchor: [0, -10],
  });
}

function Recenter({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center);
  }, [map, center]);
  return null;
}

export function RescueMap({
  listings,
  center,
  onClaim,
}: {
  listings: Listing[];
  center: [number, number];
  onClaim: (listing: Listing) => void;
}) {
  return (
    <MapContainer center={center} zoom={12} scrollWheelZoom className="h-[68vh] w-full">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Recenter center={center} />
      {listings.map((listing) => (
        <Marker
          key={listing.id}
          position={[listing.lat, listing.lng]}
          icon={pinIcon(PIN_COLORS[listing.urgency.color] ?? PIN_COLORS.slate)}
        >
          <Popup>
            <div className="min-w-[200px] space-y-2">
              <div>
                <div className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                  {categoryLabel(listing.category)}
                </div>
                <div className="text-sm font-semibold text-foreground">{listing.food_type}</div>
              </div>
              <div className="text-sm text-foreground">
                <span className="font-semibold tabular-nums">{fmtInt(listing.servings)}</span> servings ·{" "}
                {listing.urgency.label}
              </div>
              <div className="text-xs text-muted-foreground">
                {listing.donor.name} · {donorTypeLabel(listing.donor.type)}
                {listing.distance_km != null ? ` · ${listing.distance_km} km` : ""}
              </div>
              <Button size="sm" className="w-full" onClick={() => onClaim(listing)}>
                Claim pickup
              </Button>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
