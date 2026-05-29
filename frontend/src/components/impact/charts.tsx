import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { categoryLabel, fmtInt, shortDate } from "@/lib/format";
import type { CategoryBreakdown, FoodCategory, TopDonor, TrendPoint } from "@/lib/types";

const CATEGORY_COLORS: Record<FoodCategory, string> = {
  cooked: "#16A34A",
  bakery: "#F59E0B",
  produce: "#0EA5A4",
  packaged: "#64748B",
};

const axisTick = { fontSize: 12, fill: "hsl(var(--muted-foreground))" };
const gridStroke = "hsl(var(--border))";

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-lift">
      {label != null && <div className="mb-1 font-semibold text-foreground">{label}</div>}
      {payload.map((entry: any, i: number) => (
        <div key={i} className="flex items-center gap-2 text-muted-foreground">
          <span className="h-2 w-2 rounded-full" style={{ background: entry.color ?? entry.fill }} />
          <span className="text-foreground">{fmtInt(entry.value)}</span>
          <span>{entry.name}</span>
        </div>
      ))}
    </div>
  );
}

export function RescuesOverTimeChart({ data }: { data: TrendPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="mealsFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#16A34A" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#16A34A" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
        <XAxis
          dataKey="date"
          tick={axisTick}
          tickLine={false}
          axisLine={false}
          minTickGap={28}
          tickFormatter={(v) => shortDate(v)}
        />
        <YAxis tick={axisTick} tickLine={false} axisLine={false} width={44} />
        <Tooltip content={<ChartTooltip />} />
        <Area
          type="monotone"
          dataKey="meals"
          name="meals"
          stroke="#16A34A"
          strokeWidth={2.5}
          fill="url(#mealsFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function FoodByCategoryChart({ data }: { data: CategoryBreakdown[] }) {
  const rows = data.map((d) => ({ ...d, label: categoryLabel(d.category) }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={rows} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
        <XAxis dataKey="label" tick={axisTick} tickLine={false} axisLine={false} />
        <YAxis tick={axisTick} tickLine={false} axisLine={false} width={44} />
        <Tooltip cursor={{ fill: "hsl(var(--muted))", opacity: 0.4 }} content={<ChartTooltip />} />
        <Bar dataKey="servings" name="servings" radius={[6, 6, 0, 0]}>
          {rows.map((row) => (
            <Cell key={row.category} fill={CATEGORY_COLORS[row.category]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function TopDonorsChart({ data }: { data: TopDonor[] }) {
  const rows = [...data].sort((a, b) => a.meals - b.meals); // ascending -> largest on top
  return (
    <ResponsiveContainer width="100%" height={Math.max(220, rows.length * 34)}>
      <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
        <XAxis type="number" tick={axisTick} tickLine={false} axisLine={false} />
        <YAxis
          type="category"
          dataKey="name"
          tick={axisTick}
          tickLine={false}
          axisLine={false}
          width={130}
        />
        <Tooltip cursor={{ fill: "hsl(var(--muted))", opacity: 0.4 }} content={<ChartTooltip />} />
        <Bar dataKey="meals" name="meals" fill="#16A34A" radius={[0, 6, 6, 0]} barSize={16} />
      </BarChart>
    </ResponsiveContainer>
  );
}
