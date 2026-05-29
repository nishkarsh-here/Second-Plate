import { useEffect, useState } from "react";
import { countdownText } from "@/lib/format";

/** Ticking countdown to an ISO expiry. Updates every second, client-side. */
export function useCountdown(expiresIso: string): { text: string; expired: boolean } {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  const expired = new Date(expiresIso).getTime() - now <= 0;
  return { text: countdownText(expiresIso, now), expired };
}
