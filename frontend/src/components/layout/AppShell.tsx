import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { useDonors, useRecipients } from "@/lib/queries";
import { useAppState } from "@/state/appState";
import { useAuth } from "@/state/auth";
import { cn } from "@/lib/utils";

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { data: donors } = useDonors();
  const { data: recipients } = useRecipients();
  const { setRole, donorId, setDonorId, recipientId, setRecipientId, setLocation } = useAppState();
  const { user, status } = useAuth();

  // When signed in, adopt the account's role, identity and location.
  useEffect(() => {
    if (!user) return;
    setRole(user.role);
    if (user.role === "donor" && user.donor_id != null) setDonorId(user.donor_id);
    if (user.role === "recipient" && user.recipient_id != null) setRecipientId(user.recipient_id);
    if (user.lat != null && user.lng != null) setLocation({ lat: user.lat, lng: user.lng });
  }, [user, setRole, setDonorId, setRecipientId, setLocation]);

  // Guest demo: default the active identities once reference data arrives.
  useEffect(() => {
    if (status === "guest" && donorId == null && donors?.length) setDonorId(donors[0].id);
  }, [status, donors, donorId, setDonorId]);

  useEffect(() => {
    if (status === "guest" && recipientId == null && recipients?.length) {
      setRecipientId(recipients[0].id);
      setLocation({ lat: recipients[0].lat, lng: recipients[0].lng });
    }
  }, [status, recipients, recipientId, setRecipientId, setLocation]);

  return (
    <div className="min-h-screen bg-background">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-30 hidden border-r border-border bg-card/60 p-3 backdrop-blur transition-[width] duration-200 lg:flex lg:flex-col",
          collapsed ? "w-20" : "w-64",
        )}
      >
        <Sidebar collapsed={collapsed} />
      </aside>

      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent side="left" className="w-72 p-3">
          <SheetHeader className="sr-only">
            <SheetTitle>Navigation</SheetTitle>
          </SheetHeader>
          <Sidebar onNavigate={() => setMobileOpen(false)} />
        </SheetContent>
      </Sheet>

      <div
        className={cn(
          "flex min-h-screen flex-col transition-[padding] duration-200",
          collapsed ? "lg:pl-20" : "lg:pl-64",
        )}
      >
        <Topbar onMenu={() => setMobileOpen(true)} onToggleCollapse={() => setCollapsed((c) => !c)} />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
