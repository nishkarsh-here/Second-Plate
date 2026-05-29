import { useCountdown } from "@/hooks/useCountdown";
import type { UrgencyInfo } from "@/lib/types";
import { cn } from "@/lib/utils";

const STYLES: Record<string, { wrap: string; dot: string }> = {
  green: { wrap: "bg-fresh-green/10 text-fresh-green", dot: "bg-fresh-green" },
  amber: { wrap: "bg-fresh-amber/15 text-[#B45309] dark:text-fresh-amber", dot: "bg-fresh-amber" },
  rose: { wrap: "bg-fresh-rose/10 text-fresh-rose", dot: "bg-fresh-rose" },
  slate: { wrap: "bg-slate-500/10 text-slate-500", dot: "bg-slate-500" },
};

const LEVEL_WORD: Record<string, string> = {
  fresh: "Fresh",
  soon: "Expiring soon",
  critical: "Critical",
  expired: "Expired",
};

export function FreshnessBadge({
  urgency,
  expiresAt,
  className,
}: {
  urgency: UrgencyInfo;
  expiresAt: string;
  className?: string;
}) {
  const { text, expired } = useCountdown(expiresAt);
  const color = expired ? "rose" : urgency.color;
  const style = STYLES[color] ?? STYLES.slate;

  return (
    <span
      title={`${LEVEL_WORD[urgency.level] ?? urgency.level} · urgency ${urgency.score}/100`}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold tabular-nums",
        style.wrap,
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", style.dot, !expired && "animate-pulse")} />
      {expired ? "Expired" : text}
    </span>
  );
}
