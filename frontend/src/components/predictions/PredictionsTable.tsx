import { ArrowDown, ArrowUp, CalendarPlus, Info } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { donorTypeLabel, fmtInt } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { SurplusPrediction } from "@/lib/types";

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const tone = pct >= 75 ? "bg-fresh-green" : pct >= 55 ? "bg-fresh-amber" : "bg-fresh-rose";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-16 overflow-hidden rounded-full bg-muted">
        <div className={cn("h-full rounded-full", tone)} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs tabular-nums text-muted-foreground">{pct}%</span>
    </div>
  );
}

export function PredictionsTable({
  rows,
  onExplain,
  onSchedule,
}: {
  rows: SurplusPrediction[];
  onExplain: (donorId: number) => void;
  onSchedule: (p: SurplusPrediction) => void;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Donor</TableHead>
          <TableHead>Predicted tomorrow</TableHead>
          <TableHead className="hidden md:table-cell">Recent avg</TableHead>
          <TableHead>Confidence</TableHead>
          <TableHead className="hidden lg:table-cell">Top factors</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((p) => (
          <TableRow key={p.donor_id}>
            <TableCell>
              <div className="font-medium">{p.donor_name}</div>
              <div className="text-xs text-muted-foreground">{donorTypeLabel(p.donor_type)}</div>
            </TableCell>
            <TableCell>
              <span className="text-lg font-bold tabular-nums">{fmtInt(p.predicted_servings)}</span>
              <span className="ml-1 text-xs text-muted-foreground">servings</span>
            </TableCell>
            <TableCell className="hidden tabular-nums text-muted-foreground md:table-cell">
              {fmtInt(p.recent_avg_servings)}
            </TableCell>
            <TableCell>
              <ConfidenceBar value={p.confidence} />
            </TableCell>
            <TableCell className="hidden lg:table-cell">
              <div className="flex flex-wrap gap-1">
                {p.top_factors.slice(0, 2).map((f) => (
                  <Badge key={f.feature} variant="muted" className="gap-1">
                    {f.contribution >= 0 ? (
                      <ArrowUp className="h-3 w-3 text-fresh-green" />
                    ) : (
                      <ArrowDown className="h-3 w-3 text-fresh-rose" />
                    )}
                    {f.label}
                  </Badge>
                ))}
              </div>
            </TableCell>
            <TableCell className="text-right">
              <div className="flex justify-end gap-2">
                <Button size="sm" variant="ghost" onClick={() => onExplain(p.donor_id)}>
                  <Info className="h-4 w-4" />
                  Why
                </Button>
                <Button size="sm" variant="outline" onClick={() => onSchedule(p)}>
                  <CalendarPlus className="h-4 w-4" />
                  <span className="hidden sm:inline">Schedule</span>
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
