// frontend/src/pages/AuthorsPage.tsx
import { useEffect, useState } from "react";
import * as api from "@/api/admin";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface AuthorsPageProps {
  onViewAuthorPosts: (rowId: number) => void;
}

export function AuthorsPage({ onViewAuthorPosts }: AuthorsPageProps) {
  const [authors, setAuthors] = useState<api.AuthorRow[]>([]);

  useEffect(() => {
    api.getAuthors().then((res) => setAuthors(res.rows));
  }, []);

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      <h2 className="text-lg font-base">Authors with Most Unprocessed Posts</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>#</TableHead>
            <TableHead>Author</TableHead>
            <TableHead>Unprocessed Posts</TableHead>
            <TableHead className="text-right">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {authors.length === 0 ? (
            <TableRow>
              <TableCell colSpan={4} className="text-center text-foreground/60">
                No authors with more than 1 unprocessed post.
              </TableCell>
            </TableRow>
          ) : (
            authors.map((a, i) => (
              <TableRow key={a.author}>
                <TableCell>{i + 1}</TableCell>
                <TableCell>{a.author}</TableCell>
                <TableCell>
                  <Badge variant="neutral">{a.count}</Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="neutral"
                    size="xs"
                    onClick={() => onViewAuthorPosts(a.first_unprocessed_id)}
                  >
                    View posts →
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
