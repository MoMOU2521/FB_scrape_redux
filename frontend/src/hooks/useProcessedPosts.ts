// frontend/src/hooks/useProcessedPosts.ts
import { useCallback, useEffect, useState } from "react";
import * as api from "@/api/processed";
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

export function useProcessedPost(rowId: number | null) {
  const fetcher = useCallback(
    () => (rowId == null ? null : api.getProcessedPost(rowId)),
    [rowId],
  );
  return useAsyncPost<PostWithNav>(fetcher);
}

export function useAuthorProcessedPosts(rowId: number | null) {
  const fetcher = useCallback(
    () => (rowId == null ? null : api.getAuthorProcessedPosts(rowId)),
    [rowId],
  );
  return useAsyncPost<AuthorPosts>(fetcher);
}
