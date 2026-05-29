import { ClipboardList } from "lucide-react";
import { useDonorListings, useDonors } from "@/lib/queries";
import { useAppState } from "@/state/appState";
import { CreateListingForm } from "@/components/listings/CreateListingForm";
import { FreshnessBadge } from "@/components/listings/FreshnessBadge";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { categoryLabel, fmtInt, shortDate } from "@/lib/format";

const STATUS_LABEL: Record<string, string> = {
  available: "Available",
  claimed: "Claimed",
  picked_up: "Picked up",
  expired: "Expired",
};

export default function MyListings() {
  const { donorId } = useAppState();
  const { data: donors } = useDonors();
  const donor = donors?.find((d) => d.id === donorId);
  const { data, isLoading, isError, error, refetch } = useDonorListings(donorId);
  const count = data?.length ?? 0;

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-1">
        <CreateListingForm />
      </div>

      <div className="space-y-4 lg:col-span-2">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">{donor ? `${donor.name}'s listings` : "Your listings"}</h2>
          <span className="text-sm text-muted-foreground">{count} total</span>
        </div>

        {isLoading && (
          <Card>
            <CardContent className="space-y-2 p-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </CardContent>
          </Card>
        )}

        {isError && <ErrorState error={error} onRetry={() => refetch()} />}

        {!isLoading && !isError && count === 0 && (
          <EmptyState
            icon={ClipboardList}
            title="No listings yet"
            description="Post your first surplus listing with the form on the left — it'll show up here and in the live feed instantly."
          />
        )}

        {!isLoading && !isError && count > 0 && (
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Food</TableHead>
                    <TableHead>Servings</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="hidden sm:table-cell">Freshness</TableHead>
                    <TableHead className="hidden md:table-cell">Posted</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data!.map((l) => (
                    <TableRow key={l.id}>
                      <TableCell>
                        <div className="font-medium">{l.food_type}</div>
                        <div className="text-xs text-muted-foreground">{categoryLabel(l.category)}</div>
                      </TableCell>
                      <TableCell className="tabular-nums">{fmtInt(l.servings)}</TableCell>
                      <TableCell>
                        <Badge
                          variant={l.status === "available" ? "default" : "secondary"}
                          className="capitalize"
                        >
                          {STATUS_LABEL[l.status] ?? l.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="hidden sm:table-cell">
                        {l.status === "available" ? (
                          <FreshnessBadge urgency={l.urgency} expiresAt={l.expires_at} />
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell className="hidden text-sm text-muted-foreground md:table-cell">
                        {shortDate(l.created_at)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
