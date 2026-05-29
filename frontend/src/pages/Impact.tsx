import { useState } from "react";
import { Leaf, Users, Utensils, Weight } from "lucide-react";
import { useImpactSummary, useImpactTrends } from "@/lib/queries";
import { StatCard } from "@/components/impact/StatCard";
import {
  FoodByCategoryChart,
  RescuesOverTimeChart,
  TopDonorsChart,
} from "@/components/impact/charts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/common/ErrorState";
import { fmtInt } from "@/lib/format";
import { cn } from "@/lib/utils";

const RANGES = [
  { v: 30, l: "30 days" },
  { v: 90, l: "90 days" },
  { v: 180, l: "6 months" },
];

function StatSkeletons() {
  return (
    <>
      {Array.from({ length: 4 }).map((_, i) => (
        <Card key={i} className="space-y-4 p-6">
          <Skeleton className="h-11 w-11 rounded-xl" />
          <Skeleton className="h-8 w-28" />
          <Skeleton className="h-4 w-24" />
        </Card>
      ))}
    </>
  );
}

export default function Impact() {
  const [range, setRange] = useState(90);
  const summary = useImpactSummary(30);
  const trends = useImpactTrends(range);
  const s = summary.data;

  return (
    <div className="space-y-6">
      {/* KPI row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {summary.isLoading && <StatSkeletons />}
        {summary.isError && (
          <div className="sm:col-span-2 xl:col-span-4">
            <ErrorState error={summary.error} onRetry={() => summary.refetch()} />
          </div>
        )}
        {s && (
          <>
            <StatCard
              icon={Utensils}
              label="Meals rescued"
              value={fmtInt(s.meals_rescued.value)}
              delta={s.meals_rescued}
              accent="primary"
            />
            <StatCard
              icon={Weight}
              label="Food saved"
              value={`${fmtInt(s.kg_saved.value)} kg`}
              delta={s.kg_saved}
              accent="amber"
            />
            <StatCard
              icon={Leaf}
              label="CO₂e avoided"
              value={`${fmtInt(s.co2e_avoided_kg.value)} kg`}
              delta={s.co2e_avoided_kg}
              accent="sky"
            />
            <StatCard
              icon={Users}
              label="People served"
              value={fmtInt(s.people_served.value)}
              delta={s.people_served}
              accent="rose"
            />
          </>
        )}
      </div>

      {s && (
        <p className="text-sm text-muted-foreground">
          {s.active_listings} active listings · {s.total_donors} donors · {s.total_recipients}{" "}
          recipients · deltas vs. the previous {s.window_days} days.
        </p>
      )}

      {/* Trends header + range switcher */}
      <div className="flex items-center justify-between pt-2">
        <h2 className="text-lg font-semibold">Trends</h2>
        <div className="flex rounded-lg border border-border bg-card p-0.5">
          {RANGES.map((r) => (
            <button
              key={r.v}
              onClick={() => setRange(r.v)}
              className={cn(
                "rounded-md px-3 py-1.5 text-xs font-semibold transition-colors",
                range === r.v
                  ? "bg-primary text-primary-foreground shadow-soft"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {r.l}
            </button>
          ))}
        </div>
      </div>

      {trends.isError && <ErrorState error={trends.error} onRetry={() => trends.refetch()} />}

      <Card>
        <CardHeader>
          <CardTitle>Rescues over time</CardTitle>
          <CardDescription>Meals rescued per day across the selected window.</CardDescription>
        </CardHeader>
        <CardContent>
          {trends.isLoading ? (
            <Skeleton className="h-[260px] w-full rounded-xl" />
          ) : (
            <RescuesOverTimeChart data={trends.data?.series ?? []} />
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Food saved by category</CardTitle>
            <CardDescription>Total servings rescued per food category.</CardDescription>
          </CardHeader>
          <CardContent>
            {trends.isLoading ? (
              <Skeleton className="h-[260px] w-full rounded-xl" />
            ) : (
              <FoodByCategoryChart data={trends.data?.by_category ?? []} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top donors</CardTitle>
            <CardDescription>Most meals contributed in this window.</CardDescription>
          </CardHeader>
          <CardContent>
            {trends.isLoading ? (
              <Skeleton className="h-[260px] w-full rounded-xl" />
            ) : (
              <TopDonorsChart data={trends.data?.top_donors ?? []} />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
