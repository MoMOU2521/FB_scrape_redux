// frontend/src/components/posts/BuildingAliasPanel.tsx
import { useEffect, useState } from "react";
import * as api from "@/api/admin";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

export function BuildingAliasPanel() {
  const [buildings, setBuildings] = useState<api.BuildingOption[]>([]);
  const [buildingId, setBuildingId] = useState("");
  const [alias, setAlias] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    api.getBuildings().then((res) => setBuildings(res.buildings));
  }, []);

  async function add() {
    if (!buildingId || !alias.trim()) {
      setMessage("Select a building and enter alias");
      return;
    }
    const res = await api.addAlias(Number(buildingId), alias.trim());
    setMessage(res.ok ? "Alias added" : "Failed to add alias");
    if (res.ok) setAlias("");
  }

  return (
    <Card className="gap-3">
      <CardHeader>
        <CardTitle>Add Building Alias</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <select
          className="flex h-10 w-full rounded-base border-2 border-border bg-secondary-background px-3 py-2 text-sm font-base text-foreground"
          value={buildingId}
          onChange={(e) => setBuildingId(e.target.value)}
        >
          <option value="">-- select building --</option>
          {buildings.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
        <div className="flex gap-2">
          <Input
            placeholder="Raw building name from post"
            value={alias}
            onChange={(e) => setAlias(e.target.value)}
          />
          <Button size="sm" onClick={add}>
            Add Alias
          </Button>
        </div>
        {message && (
          <Alert variant="destructive">
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
