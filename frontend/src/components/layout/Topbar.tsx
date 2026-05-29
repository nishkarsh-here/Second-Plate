import { useLocation } from "react-router-dom";
import { Menu, Moon, PanelLeft, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PAGE_TITLES } from "./nav";
import { useTheme } from "@/state/theme";
import { useAppState } from "@/state/appState";
import { useDonors, useRecipients } from "@/lib/queries";
import { cn } from "@/lib/utils";

export function Topbar({
  onMenu,
  onToggleCollapse,
}: {
  onMenu: () => void;
  onToggleCollapse: () => void;
}) {
  const { pathname } = useLocation();
  const title = PAGE_TITLES[pathname] ?? "SecondPlate";
  const { theme, toggle } = useTheme();
  const { role, setRole, donorId, setDonorId, recipientId, setRecipientId, setLocation } =
    useAppState();
  const { data: donors } = useDonors();
  const { data: recipients } = useRecipients();

  const onPickDonor = (id: number) => {
    setDonorId(id);
    const d = donors?.find((x) => x.id === id);
    if (d) setLocation({ lat: d.lat, lng: d.lng });
  };
  const onPickRecipient = (id: number) => {
    setRecipientId(id);
    const r = recipients?.find((x) => x.id === id);
    if (r) setLocation({ lat: r.lat, lng: r.lng });
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur sm:px-6 lg:px-8">
      <Button variant="ghost" size="icon" className="lg:hidden" onClick={onMenu} aria-label="Open menu">
        <Menu className="h-5 w-5" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="hidden lg:inline-flex"
        onClick={onToggleCollapse}
        aria-label="Toggle sidebar"
      >
        <PanelLeft className="h-5 w-5" />
      </Button>

      <h1 className="truncate text-lg font-semibold">{title}</h1>

      <div className="ml-auto flex items-center gap-2 sm:gap-3">
        {/* Role switcher */}
        <div className="hidden rounded-lg border border-border bg-card p-0.5 sm:flex">
          {(["recipient", "donor"] as const).map((r) => (
            <button
              key={r}
              onClick={() => setRole(r)}
              className={cn(
                "rounded-md px-3 py-1.5 text-xs font-semibold capitalize transition-colors",
                role === r
                  ? "bg-primary text-primary-foreground shadow-soft"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {r === "recipient" ? "I'm a Recipient" : "I'm a Donor"}
            </button>
          ))}
        </div>

        {/* Identity picker for the active role */}
        <div className="hidden w-44 md:block">
          {role === "recipient" ? (
            <Select
              value={recipientId != null ? String(recipientId) : undefined}
              onValueChange={(v) => onPickRecipient(Number(v))}
            >
              <SelectTrigger className="h-9">
                <SelectValue placeholder="Recipient" />
              </SelectTrigger>
              <SelectContent>
                {recipients?.map((r) => (
                  <SelectItem key={r.id} value={String(r.id)}>
                    {r.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <Select
              value={donorId != null ? String(donorId) : undefined}
              onValueChange={(v) => onPickDonor(Number(v))}
            >
              <SelectTrigger className="h-9">
                <SelectValue placeholder="Donor" />
              </SelectTrigger>
              <SelectContent>
                {donors?.map((d) => (
                  <SelectItem key={d.id} value={String(d.id)}>
                    {d.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
          {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>

        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/15 text-sm font-semibold text-primary">
          {role === "recipient" ? "R" : "D"}
        </div>
      </div>
    </header>
  );
}
