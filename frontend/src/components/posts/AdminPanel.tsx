// MOCK — NOT WIRED. Blacklist / filter-phrase / db-entry endpoints don't
// exist in frontend/src/api/ yet (backend routes exist: admin.add_blacklist,
// admin.add_filter, db_entry.enter — no client wrapper for them).
// This renders the shape only. Buttons are no-ops. Circle back once
// api/admin.ts + api/dbEntry.ts exist.

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

interface AdminPanelProps {
  author: string;
}

export function AdminPanel({ author }: AdminPanelProps) {
  const [filterPhrase, setFilterPhrase] = useState("");

  return (
    <Card className="gap-4">
      <CardHeader>
        <CardTitle>Quick Admin (mock — not wired)</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <Button
          variant="neutral"
          size="sm"
          onClick={() => console.log("MOCK: blacklist", author)}
        >
          Blacklist {author}
        </Button>
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-base border-2 border-border px-3 py-1.5 text-sm"
            placeholder="Enter filter phrase..."
            value={filterPhrase}
            onChange={(e) => setFilterPhrase(e.target.value)}
          />
          <Button
            variant="neutral"
            size="sm"
            onClick={() => console.log("MOCK: add filter", filterPhrase)}
          >
            Add
          </Button>
        </div>
      </CardContent>
      <CardFooter>
        <Button size="sm" onClick={() => console.log("MOCK: enter into DB")}>
          Enter into DB
        </Button>
      </CardFooter>
    </Card>
  );
}
