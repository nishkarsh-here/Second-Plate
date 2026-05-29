import { useState } from "react";
import { CheckCircle2, RefreshCw, Sparkles } from "lucide-react";
import { usePredictions, useRetrain } from "@/lib/queries";
import { PredictionsTable } from "@/components/predictions/PredictionsTable";
import { ExplainSheet } from "@/components/predictions/ExplainSheet";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { fmtInt } from "@/lib/format";
import type { SurplusPrediction } from "@/lib/types";

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-muted/60 px-3 py-2">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-base font-semibold tabular-nums">{value}</div>
    </div>
  );
}

export default function Predictions() {
  const { data, isLoading, isError, error, refetch } = usePredictions();
  const retrain = useRetrain();
  const [explainId, setExplainId] = useState<number | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const handleSchedule = (p: SurplusPrediction) => {
    setToast(`Volunteer requested for ${p.donor_name} (~${fmtInt(p.predicted_servings)} servings tomorrow)`);
    window.setTimeout(() => setToast(null), 2800);
  };

  const m = retrain.data;

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="flex flex-col gap-4 p-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-semibold">Next-day surplus forecast</h2>
              <p className="mt-0.5 max-w-2xl text-sm text-muted-foreground">
                A GradientBoostingRegressor predicts each donor's servings for tomorrow from
                day-of-week, holiday, seasonal and rolling-average signal — so volunteers can be
                arranged before food is cooked to waste.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {m && (
              <div className="hidden gap-2 sm:flex">
                <Metric label="MAE" value={String(m.mae)} />
                <Metric label="RMSE" value={String(m.rmse)} />
                <Metric label="R²" value={String(m.r2)} />
              </div>
            )}
            <Button
              variant="outline"
              onClick={() => retrain.mutate()}
              disabled={retrain.isPending}
            >
              {retrain.isSuccess ? (
                <CheckCircle2 className="h-4 w-4 text-fresh-green" />
              ) : (
                <RefreshCw className={retrain.isPending ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
              )}
              {retrain.isPending ? "Retraining…" : "Retrain model"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {isLoading && (
            <div className="space-y-2 p-6">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          )}
          {isError && (
            <div className="p-6">
              <ErrorState error={error} onRetry={() => refetch()} />
            </div>
          )}
          {!isLoading && !isError && data && data.length > 0 && (
            <PredictionsTable rows={data} onExplain={setExplainId} onSchedule={handleSchedule} />
          )}
          {!isLoading && !isError && data && data.length === 0 && (
            <div className="p-6">
              <EmptyState
                icon={Sparkles}
                title="No predictions yet"
                description="Train the model to generate next-day forecasts."
                action={<Button onClick={() => retrain.mutate()}>Train model</Button>}
              />
            </div>
          )}
        </CardContent>
      </Card>

      <ExplainSheet donorId={explainId} onClose={() => setExplainId(null)} />

      {toast && (
        <div className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 animate-fade-in">
          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-3 text-sm shadow-lift">
            <CheckCircle2 className="h-4 w-4 text-fresh-green" />
            {toast}
          </div>
        </div>
      )}
    </div>
  );
}
