import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  Clock,
  HandHeart,
  Leaf,
  MapPin,
  Moon,
  Sparkles,
  Store,
  Sun,
  Users,
  Utensils,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/state/auth";
import { useTheme } from "@/state/theme";
import { cn } from "@/lib/utils";

const STEPS = [
  {
    icon: Store,
    title: "Donors post surplus",
    body: "Restaurants, canteens, hostels and event venues list edible surplus in seconds — type, servings, and a safe-to-eat window.",
  },
  {
    icon: HandHeart,
    title: "Recipients claim nearby",
    body: "NGOs, shelters and community kitchens browse a live feed sorted by urgency and distance, then claim a pickup.",
  },
  {
    icon: BarChart3,
    title: "Everyone sees the impact",
    body: "Meals rescued, kg of food saved and CO₂e avoided are tracked automatically and visualised in real time.",
  },
];

const FEATURES = [
  { icon: Clock, title: "Freshness-urgency scoring", body: "Every listing gets a live green / amber / rose badge from time-to-expiry, servings and category perishability." },
  { icon: MapPin, title: "Live rescue map", body: "See active rescues near you on an interactive map with colour-coded pins, and claim straight from the popup." },
  { icon: Sparkles, title: "Surplus forecasting", body: "A gradient-boosting model predicts each donor's next-day surplus so volunteers can be arranged in advance." },
  { icon: BarChart3, title: "Impact dashboard", body: "Trends over time, breakdowns by food category, and top donors — all from real aggregated data." },
  { icon: Leaf, title: "Real environmental math", body: "Food saved is converted to CO₂e avoided, so impact is measured in outcomes, not vanity metrics." },
  { icon: Users, title: "Donor & recipient accounts", body: "Sign up as either side and act as your own organisation — or explore the whole thing as a guest." },
];

export default function Landing() {
  const navigate = useNavigate();
  const { theme, toggle } = useTheme();
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-20 border-b border-border bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-3 px-4 sm:px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-soft">
              <Utensils className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold">SecondPlate</span>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
              {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>
            {user ? (
              <>
                <Button variant="outline" size="sm" onClick={logout}>
                  Log out
                </Button>
                <Button size="sm" onClick={() => navigate("/browse")}>
                  Open dashboard
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" size="sm" onClick={() => navigate("/login")}>
                  Log in
                </Button>
                <Button size="sm" onClick={() => navigate("/login?signup=1")}>
                  Sign up
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-4 pb-8 pt-14 sm:px-6 sm:pt-20">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <div>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
              <Leaf className="h-3.5 w-3.5" /> Rescue food, fight hunger
            </span>
            <h1 className="mt-4 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">
              Rescue surplus food <span className="text-primary">before it spoils.</span>
            </h1>
            <p className="mt-4 max-w-xl text-lg text-muted-foreground">
              SecondPlate connects food donors with nearby NGOs, shelters and community kitchens —
              and forecasts tomorrow's surplus so good food reaches a plate instead of a bin.
            </p>
            <div className="mt-7 flex flex-col gap-3 sm:flex-row">
              {user ? (
                <Button size="lg" onClick={() => navigate("/browse")}>
                  Open your dashboard <ArrowRight className="h-4 w-4" />
                </Button>
              ) : (
                <>
                  <Button size="lg" onClick={() => navigate("/login?signup=1")}>
                    Get started — it's free <ArrowRight className="h-4 w-4" />
                  </Button>
                  <Button size="lg" variant="outline" onClick={() => navigate("/browse")}>
                    Continue as guest
                  </Button>
                </>
              )}
            </div>
            {!user && (
              <p className="mt-3 text-sm text-muted-foreground">
                Already have an account?{" "}
                <button
                  onClick={() => navigate("/login")}
                  className="font-semibold text-primary hover:underline"
                >
                  Log in
                </button>
              </p>
            )}
          </div>

          {/* Decorative product preview */}
          <div className="relative">
            <div className="rounded-2xl border border-border bg-card p-6 shadow-lift">
              <div className="flex items-start justify-between">
                <span className="rounded-full bg-muted px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">
                  Cooked meals
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-fresh-green/10 px-2.5 py-1 text-xs font-semibold text-fresh-green">
                  <span className="h-1.5 w-1.5 rounded-full bg-fresh-green" /> 2h 14m left
                </span>
              </div>
              <h3 className="mt-3 text-base font-semibold">Vegetable biryani</h3>
              <div className="mt-2 flex items-end gap-2">
                <span className="text-3xl font-bold tabular-nums">40</span>
                <span className="pb-0.5 text-sm text-muted-foreground">servings</span>
                <Utensils className="ml-auto h-5 w-5 text-primary/70" />
              </div>
              <div className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
                <Store className="h-4 w-4" /> Spice Garden · 1.2 km away
              </div>
              <div className="mt-4 h-10 rounded-lg bg-primary text-center text-sm font-medium leading-10 text-primary-foreground">
                Claim pickup
              </div>
            </div>
            <div className="absolute -bottom-5 -left-5 hidden rounded-2xl border border-border bg-card px-4 py-3 shadow-lift sm:block">
              <div className="text-xs text-muted-foreground">Meals rescued</div>
              <div className="text-2xl font-bold tabular-nums text-primary">12,480</div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="text-center text-2xl font-bold">How it works</h2>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {STEPS.map((s, i) => (
            <div key={s.title} className="rounded-2xl border border-border bg-card p-6 shadow-soft">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <s.icon className="h-5 w-5" />
              </div>
              <div className="mt-4 text-xs font-semibold text-muted-foreground">STEP {i + 1}</div>
              <h3 className="mt-1 font-semibold">{s.title}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground">{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="border-y border-border bg-muted/30">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
          <h2 className="text-center text-2xl font-bold">Everything you need to rescue food</h2>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => (
              <div key={f.title} className="rounded-2xl border border-border bg-card p-6 shadow-soft">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 font-semibold">{f.title}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA band */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <div className="rounded-2xl bg-primary px-6 py-12 text-center text-primary-foreground shadow-lift sm:px-12">
          <h2 className="text-2xl font-bold sm:text-3xl">Ready to turn surplus into second plates?</h2>
          <p className="mx-auto mt-2 max-w-xl text-primary-foreground/90">
            Join as a donor or a recipient — or jump straight in and explore the live demo.
          </p>
          <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
            <Button
              size="lg"
              variant="secondary"
              onClick={() => navigate(user ? "/browse" : "/login?signup=1")}
            >
              {user ? "Open dashboard" : "Create an account"} <ArrowRight className="h-4 w-4" />
            </Button>
            <Button
              size="lg"
              onClick={() => navigate("/browse")}
              className="border border-primary-foreground/30 bg-primary-foreground/10 text-primary-foreground hover:bg-primary-foreground/20"
            >
              Continue as guest
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 py-8 text-sm text-muted-foreground sm:flex-row sm:px-6">
          <div className="flex items-center gap-2">
            <Utensils className="h-4 w-4 text-primary" />
            <span className="font-semibold text-foreground">SecondPlate</span>
            <span>· rescuing surplus food</span>
          </div>
          <div className={cn("flex items-center gap-4")}>
            <a
              href="https://github.com/Yuvraj0208/secondplate"
              target="_blank"
              rel="noreferrer"
              className="hover:text-foreground"
            >
              GitHub
            </a>
            <button onClick={() => navigate("/browse")} className="hover:text-foreground">
              Live demo
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
