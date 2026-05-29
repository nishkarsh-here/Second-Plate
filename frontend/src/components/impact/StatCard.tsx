import { ArrowDownRight, ArrowUpRight, Minus, type LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { fmtDelta } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { StatDelta } from "@/lib/types";

type Accent = "primary" | "amber" | "rose" | "sky";

const ACCENTS: Record<Accent, string> = {
  primary: "bg-primary/10 text-primary",
  amber: "bg-fresh-amber/15 text-[#B45309] dark:text-fresh-amber",
  rose: "bg-fresh-rose/10 text-fresh-rose",
  sky: "bg-sky-500/10 text-sky-600 dark:text-sky-400",
};

export function StatCard({
  icon: Icon,
  label,
  value,
  delta,
  accent = "primary",
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  delta?: StatDelta | null;
  accent?: Accent;
}) {
  const d = delta ? fmtDelta(delta.delta_pct) : null;

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div className={cn("flex h-11 w-11 items-center justify-center rounded-xl", ACCENTS[accent])}>
          <Icon className="h-5 w-5" />
        </div>
        {d &&
          (d.dir === "flat" ? (
            <span className="inline-flex items-center gap-0.5 text-xs font-medium text-muted-foreground">
              <Minus className="h-3.5 w-3.5" />
              {d.text}
            </span>
          ) : (
            <span
              className={cn(
                "inline-flex items-center gap-0.5 text-xs font-semibold",
                d.dir === "up" ? "text-fresh-green" : "text-fresh-rose",
              )}
              title="vs. previous period"
            >
              {d.dir === "up" ? (
                <ArrowUpRight className="h-3.5 w-3.5" />
              ) : (
                <ArrowDownRight className="h-3.5 w-3.5" />
              )}
              {d.text}
            </span>
          ))}
      </div>
      <div className="mt-4 text-3xl font-bold tabular-nums tracking-tight">{value}</div>
      <div className="mt-1 text-sm text-muted-foreground">{label}</div>
    </Card>
  );
}
