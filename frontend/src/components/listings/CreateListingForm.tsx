import { useState } from "react";
import { CheckCircle2, PlusCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
import { useCreateListing, useDonors } from "@/lib/queries";
import { apiErrorMessage } from "@/lib/api";
import { useAppState } from "@/state/appState";
import type { FoodCategory } from "@/lib/types";

const CATEGORIES: { value: FoodCategory; label: string }[] = [
  { value: "cooked", label: "Cooked meals" },
  { value: "bakery", label: "Bakery" },
  { value: "produce", label: "Produce" },
  { value: "packaged", label: "Packaged" },
];

function toLocalInputValue(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(
    d.getMinutes(),
  )}`;
}

export function CreateListingForm() {
  const { donorId } = useAppState();
  const { data: donors } = useDonors();
  const donor = donors?.find((d) => d.id === donorId);
  const create = useCreateListing();

  const now = new Date();
  const [foodType, setFoodType] = useState("");
  const [category, setCategory] = useState<FoodCategory>("cooked");
  const [servings, setServings] = useState("");
  const [prepared, setPrepared] = useState(toLocalInputValue(now));
  const [expires, setExpires] = useState(toLocalInputValue(new Date(now.getTime() + 4 * 3600 * 1000)));
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [ok, setOk] = useState(false);

  const validate = () => {
    const e: Record<string, string> = {};
    if (foodType.trim().length < 2) e.foodType = "Enter a food name";
    const sv = Number(servings);
    if (!sv || sv <= 0) e.servings = "Must be greater than 0";
    if (new Date(expires) <= new Date(prepared)) e.expires = "Must be after the prepared time";
    if (donorId == null) e.donor = "Choose a donor in the top bar first";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const submit = (ev: React.FormEvent) => {
    ev.preventDefault();
    setOk(false);
    if (!validate()) return;
    create.mutate(
      {
        donor_id: donorId as number,
        food_type: foodType.trim(),
        category,
        servings: Number(servings),
        prepared_at: new Date(prepared).toISOString(),
        expires_at: new Date(expires).toISOString(),
      },
      {
        onSuccess: () => {
          setOk(true);
          setFoodType("");
          setServings("");
          window.setTimeout(() => setOk(false), 3500);
        },
      },
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Post surplus food</CardTitle>
        <CardDescription>
          {donor ? `Posting as ${donor.name}` : "Select a donor in the top bar"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={submit} className="space-y-4" noValidate>
          <div className="space-y-1.5">
            <Label htmlFor="food">Food type</Label>
            <Input
              id="food"
              placeholder="e.g. Vegetable biryani"
              value={foodType}
              onChange={(e) => setFoodType(e.target.value)}
            />
            {errors.foodType && <p className="text-xs text-fresh-rose">{errors.foodType}</p>}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Category</Label>
              <Select value={category} onValueChange={(v) => setCategory(v as FoodCategory)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map((c) => (
                    <SelectItem key={c.value} value={c.value}>
                      {c.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="servings">Servings</Label>
              <Input
                id="servings"
                type="number"
                min={1}
                placeholder="40"
                value={servings}
                onChange={(e) => setServings(e.target.value)}
              />
              {errors.servings && <p className="text-xs text-fresh-rose">{errors.servings}</p>}
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="prepared">Prepared at</Label>
            <Input
              id="prepared"
              type="datetime-local"
              value={prepared}
              onChange={(e) => setPrepared(e.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="expires">Safe to consume until</Label>
            <Input
              id="expires"
              type="datetime-local"
              value={expires}
              onChange={(e) => setExpires(e.target.value)}
            />
            {errors.expires && <p className="text-xs text-fresh-rose">{errors.expires}</p>}
          </div>

          {errors.donor && <p className="text-xs text-fresh-rose">{errors.donor}</p>}
          {create.isError && <p className="text-xs text-fresh-rose">{apiErrorMessage(create.error)}</p>}

          <Button type="submit" className="w-full" disabled={create.isPending}>
            {ok ? <CheckCircle2 className="h-4 w-4" /> : <PlusCircle className="h-4 w-4" />}
            {create.isPending ? "Posting…" : ok ? "Listing posted!" : "Post listing"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
