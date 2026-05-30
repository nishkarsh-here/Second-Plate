import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Utensils } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/state/auth";
import { apiErrorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { AuthRole, DonorType, RecipientType } from "@/lib/types";

const DONOR_TYPES: { value: DonorType; label: string }[] = [
  { value: "restaurant", label: "Restaurant" },
  { value: "canteen", label: "Canteen" },
  { value: "hostel", label: "Hostel" },
  { value: "event", label: "Event venue" },
];

const RECIPIENT_TYPES: { value: RecipientType; label: string }[] = [
  { value: "ngo", label: "NGO" },
  { value: "shelter", label: "Shelter" },
  { value: "community_kitchen", label: "Community kitchen" },
];

export default function Login() {
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const [mode, setMode] = useState<"login" | "signup">("login");
  const [role, setRole] = useState<AuthRole>("recipient");
  const [name, setName] = useState("");
  const [orgType, setOrgType] = useState<string>("ngo");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const switchRole = (r: AuthRole) => {
    setRole(r);
    setOrgType(r === "donor" ? "restaurant" : "ngo");
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register({
          email,
          password,
          name,
          role,
          ...(role === "donor"
            ? { donor_type: orgType as DonorType }
            : { recipient_type: orgType as RecipientType }),
        });
      }
      navigate("/");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const types = role === "donor" ? DONOR_TYPES : RECIPIENT_TYPES;

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-soft">
            <Utensils className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold">SecondPlate</h1>
          <p className="text-sm text-muted-foreground">Rescue surplus food before it spoils</p>
        </div>

        <Card>
          <CardContent className="p-6">
            <div className="mb-5 flex rounded-lg border border-border bg-muted/40 p-0.5">
              {(["login", "signup"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => {
                    setMode(m);
                    setError(null);
                  }}
                  className={cn(
                    "flex-1 rounded-md px-3 py-2 text-sm font-semibold transition-colors",
                    mode === m
                      ? "bg-card text-foreground shadow-soft"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  {m === "login" ? "Sign in" : "Create account"}
                </button>
              ))}
            </div>

            <form onSubmit={submit} className="space-y-4" noValidate>
              {mode === "signup" && (
                <>
                  <div className="space-y-1.5">
                    <Label>I am a</Label>
                    <div className="flex rounded-lg border border-border bg-card p-0.5">
                      {(["recipient", "donor"] as const).map((r) => (
                        <button
                          key={r}
                          type="button"
                          onClick={() => switchRole(r)}
                          className={cn(
                            "flex-1 rounded-md px-3 py-2 text-sm font-semibold capitalize transition-colors",
                            role === r
                              ? "bg-primary text-primary-foreground shadow-soft"
                              : "text-muted-foreground hover:text-foreground",
                          )}
                        >
                          {r}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <Label htmlFor="name">Organisation name</Label>
                      <Input
                        id="name"
                        placeholder={role === "donor" ? "Spice Garden" : "Hope Foundation"}
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label>Type</Label>
                      <Select value={orgType} onValueChange={setOrgType}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {types.map((t) => (
                            <SelectItem key={t.value} value={t.value}>
                              {t.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </>
              )}

              <div className="space-y-1.5">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="At least 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              {error && <p className="text-sm text-fresh-rose">{error}</p>}

              <Button type="submit" className="w-full" disabled={busy}>
                {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
              </Button>
            </form>

            <button
              type="button"
              onClick={() => navigate("/")}
              className="mt-4 w-full text-center text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              or explore the live demo as a guest →
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
