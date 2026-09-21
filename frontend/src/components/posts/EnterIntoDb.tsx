import { useState } from "react";
import * as api from "@/api/entry";
import { Button } from "@/components/ui/button";

interface EnterIntoDbProps {
  rowId: number;
  onDone: () => void;
}

export function EnterIntoDb({ rowId, onDone }: EnterIntoDbProps) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function enter() {
    setBusy(true);
    setMessage("Processing...");
    try {
      const res = await api.enterPost(rowId);
      if (res.decision === "discard") {
        setMessage("Skipped: exact duplicate exists.");
      } else if (res.decision === "review") {
        setMessage(
          `Sent to review (candidate ID: ${res.candidate_property_id})`,
        );
      } else {
        setMessage(`Entered! Property ID: ${res.property_id}`);
      }
      await new Promise((r) => setTimeout(r, 1000));
      setMessage(null);
      onDone();
    } catch (e) {
      setMessage((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex items-center gap-3">
      <Button size="sm" onClick={enter} disabled={busy}>
        Enter into DB
      </Button>
      {message && <span className="text-sm">{message}</span>}
    </div>
  );
}
