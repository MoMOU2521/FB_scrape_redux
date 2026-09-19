import { useEffect, useState } from "react";
import * as api from "@/api/admin";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Message = { text: string; variant: "default" | "destructive" };

export function FiltersPage() {
  const [rows, setRows] = useState<api.FilterRow[]>([]);
  const [newPhrase, setNewPhrase] = useState("");
  const [message, setMessage] = useState<Message | null>(null);

  function refresh() {
    api.getFilters().then((res) => setRows(res.rows));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function add() {
    const phrase = newPhrase.trim();
    if (!phrase) {
      setMessage({ text: "Enter a phrase first", variant: "destructive" });
      return;
    }
    const res = await api.addFilterPhrase(phrase);
    setMessage(
      res.already_exists
        ? {
            text: "Phrase already exists in filter list",
            variant: "destructive",
          }
        : null,
    );
    if (!res.already_exists) setNewPhrase("");
    refresh();
  }

  async function remove(phrase: string) {
    if (!confirm(`Remove "${phrase}" from filter phrases?`)) return;
    await api.deleteFilterPhrase(phrase);
    refresh();
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      <h2 className="text-lg font-base">Filter Phrases</h2>

      <div className="flex gap-2">
        <Input
          placeholder="Phrase to filter"
          value={newPhrase}
          onChange={(e) => setNewPhrase(e.target.value)}
        />
        <Button size="sm" onClick={add}>
          Add
        </Button>
      </div>

      {message && (
        <Alert variant={message.variant}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Phrase</TableHead>
            <TableHead>Added At</TableHead>
            <TableHead className="text-right">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length === 0 ? (
            <TableRow>
              <TableCell colSpan={3} className="text-center text-foreground/60">
                No filter phrases.
              </TableCell>
            </TableRow>
          ) : (
            rows.map((r) => (
              <TableRow key={r.phrase}>
                <TableCell>{r.phrase}</TableCell>
                <TableCell className="text-foreground/60">
                  {r.added_at ?? "N/A"}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="neutral"
                    size="xs"
                    onClick={() => remove(r.phrase)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
