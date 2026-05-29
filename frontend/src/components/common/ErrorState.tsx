import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiErrorMessage } from "@/lib/api";

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-fresh-rose/40 bg-fresh-rose/5 px-6 py-14 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-fresh-rose/10 text-fresh-rose">
        <AlertTriangle className="h-7 w-7" />
      </div>
      <h3 className="text-base font-semibold">Couldn't load this</h3>
      <p className="mt-1 max-w-sm text-sm text-muted-foreground">{apiErrorMessage(error)}</p>
      {onRetry && (
        <Button variant="outline" className="mt-5" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
