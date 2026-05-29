import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { useExplain } from "@/lib/queries";
import { fmtInt } from "@/lib/format";
import { cn } from "@/lib/utils";

export function ExplainSheet({ donorId, onClose }: { donorId: number | null; onClose: () => void }) {
  const { data, isLoading } = useExplain(donorId);
  const maxAbs = data ? Math.max(...data.factors.map((f) => Math.abs(f.contribution)), 1) : 1;

  return (
    <Sheet open={donorId != null} onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="right" className="overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Why this prediction?</SheetTitle>
          <SheetDescription>
            How each feature moves tomorrow's forecast for this donor, relative to the model's
            baseline (one-at-a-time ablation).
          </SheetDescription>
        </SheetHeader>

        {isLoading && (
          <div className="mt-4 space-y-3">
            <Skeleton className="h-24 w-full rounded-xl" />
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        )}

        {data && (
          <div className="mt-4">
            <div className="rounded-xl bg-muted/60 p-4">
              <div className="text-sm font-medium">{data.donor_name}</div>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="text-3xl font-bold tabular-nums">
                  {fmtInt(data.predicted_servings)}
                </span>
                <span className="text-sm text-muted-foreground">servings predicted tomorrow</span>
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                Confidence {Math.round(data.confidence * 100)}%
              </div>
            </div>

            <div className="mt-5 space-y-3.5">
              {data.factors.map((f) => {
                const positive = f.contribution >= 0;
                const width = (Math.abs(f.contribution) / maxAbs) * 100;
                return (
                  <div key={f.feature}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{f.label}</span>
                      <span
                        className={cn(
                          "font-semibold tabular-nums",
                          positive ? "text-fresh-green" : "text-fresh-rose",
                        )}
                      >
                        {positive ? "+" : ""}
                        {f.contribution}
                      </span>
                    </div>
                    <div className="mt-1 h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className={cn("h-full rounded-full", positive ? "bg-fresh-green" : "bg-fresh-rose")}
                        style={{ width: `${width}%` }}
                      />
                    </div>
                    <div className="mt-0.5 flex justify-between text-xs text-muted-foreground">
                      <span>value {f.value}</span>
                      <span>importance {Math.round(f.importance * 100)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-5 border-t border-border pt-3 text-xs text-muted-foreground">
              Model {data.model_version}
              {data.trained_at && ` · trained ${new Date(data.trained_at).toLocaleString()}`}
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
