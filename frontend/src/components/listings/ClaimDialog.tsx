import { useEffect, useState } from "react";
import { CheckCircle2, PackageCheck } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useClaimListing, useRecipients } from "@/lib/queries";
import { apiErrorMessage } from "@/lib/api";
import { recipientTypeLabel, fmtInt } from "@/lib/format";
import { useAppState } from "@/state/appState";
import type { Listing } from "@/lib/types";

export function ClaimDialog({ listing, onClose }: { listing: Listing | null; onClose: () => void }) {
  const { data: recipients } = useRecipients();
  const { recipientId } = useAppState();
  const claim = useClaimListing();
  const [selected, setSelected] = useState<number | null>(recipientId);
  const [done, setDone] = useState(false);

  useEffect(() => {
    setSelected(recipientId);
    setDone(false);
    claim.reset();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listing, recipientId]);

  const handleConfirm = () => {
    if (!listing || selected == null) return;
    claim.mutate(
      { id: listing.id, recipientId: selected },
      { onSuccess: () => { setDone(true); window.setTimeout(onClose, 1300); } },
    );
  };

  return (
    <Dialog open={!!listing} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        {listing && !done && (
          <>
            <DialogHeader>
              <DialogTitle>Claim this rescue</DialogTitle>
              <DialogDescription>
                Schedule a pickup for <span className="font-medium text-foreground">{listing.food_type}</span>{" "}
                ({fmtInt(listing.servings)} servings) from {listing.donor.name}.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-2">
              <Label htmlFor="recipient">Claiming as</Label>
              <Select
                value={selected != null ? String(selected) : undefined}
                onValueChange={(v) => setSelected(Number(v))}
              >
                <SelectTrigger id="recipient">
                  <SelectValue placeholder="Select a recipient organisation" />
                </SelectTrigger>
                <SelectContent>
                  {recipients?.map((r) => (
                    <SelectItem key={r.id} value={String(r.id)}>
                      {r.name} · {recipientTypeLabel(r.type)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {claim.isError && (
              <p className="text-sm text-fresh-rose">{apiErrorMessage(claim.error)}</p>
            )}

            <DialogFooter>
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button onClick={handleConfirm} disabled={selected == null || claim.isPending}>
                <PackageCheck className="h-4 w-4" />
                {claim.isPending ? "Scheduling…" : "Confirm pickup"}
              </Button>
            </DialogFooter>
          </>
        )}

        {listing && done && (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-fresh-green/10 text-fresh-green">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <DialogTitle>Pickup scheduled</DialogTitle>
            <DialogDescription>
              {fmtInt(listing.servings)} servings of {listing.food_type} are on their way to a plate
              instead of the bin.
            </DialogDescription>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
