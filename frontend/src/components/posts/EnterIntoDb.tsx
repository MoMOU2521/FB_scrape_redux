import { useState } from "react";
import * as api from "@/api/entry";
import { Button } from "@/components/ui/button";

interface EnterIntoDbProps {
  rowId: number;
  onDone: () => void;
}

export function EnterIntoDb({ rowId, onDone }: EnterIntoDbProps) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function enter() {
    setBusy(true);
    setError(null);
    try {
      await api.enterPost(rowId);
      onDone();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex items-center gap-3">
      <Button size="sm" onClick={enter} disabled={busy}>
        Enter into DB
      </Button>
      {error && <span className="text-sm">{error}</span>}
    </div>
  );
}
