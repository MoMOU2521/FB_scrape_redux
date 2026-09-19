// frontend/src/pages/StatsPage.tsx
import { useEffect, useState } from "react";
import * as api from "@/api/admin";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";

interface StatsPageProps {
  onViewAuthorPosts: (rowId: number) => void;
}

export function StatsPage({ onViewAuthorPosts }: StatsPageProps) {
  const [stats, setStats] = useState<api.StatsResponse | null>(null);
  const [authors, setAuthors] = useState<api.AuthorRow[]>([]);

  useEffect(() => {
    api.getStats().then(setStats);
    api.getAuthors().then((res) => setAuthors(res.rows));
  }, []);

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 p-6">
      <div>
        <h2 className="mb-3 text-lg font-base">Group Statistics</h2>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Group Name</TableHead>
              <TableHead>Total Posts</TableHead>
              <TableHead>Selected</TableHead>
              <TableHead>Selection Rate</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {stats?.groups.map((g) => (
              <TableRow key={g.group_name}>
                <TableCell>{g.group_name}</TableCell>
                <TableCell>{g.total}</TableCell>
                <TableCell>{g.selected}</TableCell>
                <TableCell>{g.rate}%</TableCell>
              </TableRow>
            ))}
            {stats && (
              <TableRow>
                <TableCell className="font-base">TOTAL</TableCell>
                <TableCell className="font-base">{stats.total_posts}</TableCell>
                <TableCell className="font-base">
                  {stats.total_selected}
                </TableCell>
                <TableCell className="font-base">{stats.total_rate}%</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <div>
        <h2 className="mb-3 text-lg font-base">
          Authors with Most Unprocessed Posts
        </h2>
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
                <TableCell
                  colSpan={4}
                  className="text-center text-foreground/60"
                >
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
    </div>
  );
}
