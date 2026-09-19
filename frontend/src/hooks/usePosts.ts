// frontend/src/hooks/usePosts.ts
import { useCallback, useEffect, useState } from "react";
import * as api from "@/api/posts";
import type { PostWithNav, AuthorPosts } from "@/api/posts";

type Status = "idle" | "loading" | "error";

function useAsyncPost<T>(fetcher: () => Promise<T> | null) {
  const [data, setData] = useState<T | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(() => {
    const p = fetcher();
    if (!p) {
      setData(null);
      setStatus("idle");
      return;
    }
    setStatus("loading");
    setError(null);
    p.then((res) => {
      setData(res);
      setStatus("idle");
    }).catch((e: Error) => {
      setData(null);
      setError(e.message);
      setStatus("error");
    });
  }, [fetcher]);

  useEffect(() => {
    refetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refetch]);

  return { data, loading: status === "loading", error, refetch };
}

export function usePost(rowId: number | null) {
  const fetcher = useCallback(
    () => (rowId == null ? null : api.getPost(rowId)),
    [rowId],
  );
  return useAsyncPost<PostWithNav>(fetcher);
}

export function useAuthorPosts(rowId: number | null) {
  const fetcher = useCallback(
    () => (rowId == null ? null : api.getAuthorPosts(rowId)),
    [rowId],
  );
  return useAsyncPost<AuthorPosts>(fetcher);
}

/**
 * Mutations shared by both fifo and author views. Callers pass their own
 * refetch (from usePost/useAuthorPosts) so the mutation and the view
 * that should refresh after it stay decoupled from each other.
 */
export function usePostActions(rowId: number | null, onChanged?: () => void) {
  const markProcessed = useCallback(
    async (processed: 0 | 1) => {
      if (rowId == null) return;
      await api.markProcessed(rowId, processed);
    },
    [rowId],
  );

  const toggleSelected = useCallback(
    async (selected: 0 | 1) => {
      if (rowId == null) return;
      await api.toggleSelected(rowId, selected);
      onChanged?.();
    },
    [rowId, onChanged],
  );

  const remove = useCallback(async () => {
    if (rowId == null) return false;
    const res = await api.deletePost(rowId);
    return res.ok;
  }, [rowId]);

  return { markProcessed, toggleSelected, remove };
}
