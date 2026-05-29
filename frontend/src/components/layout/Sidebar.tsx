import { NavLink } from "react-router-dom";
import { Utensils } from "lucide-react";
import { NAV_ITEMS } from "./nav";
import { cn } from "@/lib/utils";

export function Sidebar({
  collapsed = false,
  onNavigate,
}: {
  collapsed?: boolean;
  onNavigate?: () => void;
}) {
  return (
    <div className="flex h-full flex-col gap-2">
      <div className={cn("flex items-center gap-2.5 px-2 py-1", collapsed && "justify-center px-0")}>
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-soft">
          <Utensils className="h-5 w-5" />
        </div>
        {!collapsed && (
          <div className="leading-tight">
            <div className="font-bold">SecondPlate</div>
            <div className="text-xs text-muted-foreground">Rescue surplus food</div>
          </div>
        )}
      </div>

      <nav className="mt-3 flex flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            title={collapsed ? item.label : undefined}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                collapsed && "justify-center px-0",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <div className="mt-auto rounded-xl bg-muted/60 p-3 text-xs leading-relaxed text-muted-foreground">
          Demo data. Switch roles in the top bar to post listings as a donor or claim them as a
          recipient.
        </div>
      )}
    </div>
  );
}
