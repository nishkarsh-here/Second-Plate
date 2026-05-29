import { createContext, useContext, useState, type ReactNode } from "react";

export type Role = "donor" | "recipient";

interface AppStateValue {
  role: Role;
  setRole: (r: Role) => void;
  /** Active donor identity (donor mode: My Listings + create form). */
  donorId: number | null;
  setDonorId: (id: number | null) => void;
  /** Active recipient identity (recipient mode: claims). */
  recipientId: number | null;
  setRecipientId: (id: number | null) => void;
  /** Viewer location used for distance sorting in Browse / Map. */
  location: { lat: number; lng: number };
  setLocation: (loc: { lat: number; lng: number }) => void;
}

// Central Bengaluru — matches the seeded data's geography.
export const DEFAULT_LOCATION = { lat: 12.9716, lng: 77.5946 };

const AppStateContext = createContext<AppStateValue | null>(null);

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>("recipient");
  const [donorId, setDonorId] = useState<number | null>(null);
  const [recipientId, setRecipientId] = useState<number | null>(null);
  const [location, setLocation] = useState(DEFAULT_LOCATION);

  return (
    <AppStateContext.Provider
      value={{ role, setRole, donorId, setDonorId, recipientId, setRecipientId, location, setLocation }}
    >
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState(): AppStateValue {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error("useAppState must be used within AppStateProvider");
  return ctx;
}
