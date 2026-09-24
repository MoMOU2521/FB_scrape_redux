import { useEffect, useState } from "react";
import * as api from "@/api/admin";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
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

export function BlacklistPage() {
  const [rows, setRows] = useState<api.BlacklistRow[]>([]);
  const [sort, setSort] = useState<"count" | "alpha">("count");
  const [newAuthor, setNewAuthor] = useState("");
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState<Message | null>(null);

  function refresh(s: "count" | "alpha" = sort) {
    api.getBlacklist(s).then((res) => setRows(res.rows));
  }

  useEffect(() => {
    refresh(sort);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sort]);

  async function add() {
    const author = newAuthor.trim();
    if (!author) {
      setMessage({ text: "Enter a name first", variant: "destructive" });
      return;
    }
    try {
      await api.addBlacklist(author);
      setNewAuthor("");
      setMessage(null);
      refresh();
    } catch (e) {
      setMessage({ text: (e as Error).message, variant: "destructive" });
    }
  }

  async function remove(author: string) {
    if (!confirm(`Remove "${author}" from blacklist?`)) return;
    await api.deleteBlacklist(author);
    refresh();
  }

  const filteredRows = rows.filter((r) =>
    r.author.toLowerCase().includes(search.trim().toLowerCase()),
  );

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      <div className="flex items-center gap-2">
        <h2 className="text-lg font-base">Blacklisted Authors</h2>
        <div className="ml-auto flex gap-2">
          <Button
            variant={sort === "count" ? "default" : "neutral"}
            size="xs"
            onClick={() => setSort("count")}
          >
            Count
          </Button>
          <Button
            variant={sort === "alpha" ? "default" : "neutral"}
            size="xs"
            onClick={() => setSort("alpha")}
          >
            Alphabetical
          </Button>
        </div>
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="Author name"
          value={newAuthor}
          onChange={(e) => setNewAuthor(e.target.value)}
        />
        <Button size="sm" onClick={add}>
          Add
        </Button>
      </div>

      <Input
        placeholder="Search by author"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {message && (
        <Alert variant={message.variant}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Author</TableHead>
            <TableHead>Count</TableHead>
            <TableHead className="text-right">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredRows.length === 0 ? (
            <TableRow>
              <TableCell colSpan={3} className="text-center text-foreground/60">
                No blacklisted authors.
              </TableCell>
            </TableRow>
          ) : (
            filteredRows.map((r) => (
              <TableRow key={r.author}>
                <TableCell>{r.author}</TableCell>
                <TableCell>
                  <Badge variant="neutral">{r.count}</Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="neutral"
                    size="xs"
                    onClick={() => remove(r.author)}
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
