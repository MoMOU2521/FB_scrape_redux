import { useState } from "react";
import * as api from "@/api/admin";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface AdminPanelProps {
  author: string;
  onBlacklisted: () => void;
}

export function AdminPanel({ author, onBlacklisted }: AdminPanelProps) {
  const [filterPhrase, setFilterPhrase] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  async function blacklist() {
    setMessage(null);
    try {
      await api.addBlacklist(author);
      onBlacklisted();
    } catch (e) {
      setMessage((e as Error).message);
    }
  }

  async function addFilter() {
    const phrase = filterPhrase.trim();
    if (!phrase) {
      setMessage("Enter a phrase first");
      return;
    }
    try {
      const res = await api.addFilterPhrase(phrase);
      setMessage(
        res.already_exists ? "Phrase already exists" : "Filter phrase added",
      );
      if (!res.already_exists) setFilterPhrase("");
    } catch (e) {
      setMessage((e as Error).message);
    }
  }

  return (
    <Card className="gap-4">
      <CardHeader>
        <CardTitle>Quick Admin</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <Button variant="neutral" size="sm" onClick={blacklist}>
          Blacklist {author}
        </Button>
        <div className="flex gap-2">
          <Input
            placeholder="Enter filter phrase..."
            value={filterPhrase}
            onChange={(e) => setFilterPhrase(e.target.value)}
          />
          <Button variant="neutral" size="sm" onClick={addFilter}>
            Add
          </Button>
        </div>
        {message && (
          <Alert variant="destructive">
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}{" "}
      </CardContent>
    </Card>
  );
}
