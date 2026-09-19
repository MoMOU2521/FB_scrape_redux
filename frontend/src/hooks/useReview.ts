// frontend/src/hooks/useReview.ts
import { useCallback, useEffect, useState } from "react";
import * as api from "@/api/review";
import type { ReviewWithNav } from "@/api/review";

type Status = "idle" | "loading" | "error";

export function useReview(reviewId: number | null) {
  const [data, setData] = useState<ReviewWithNav | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(() => {
    if (reviewId == null) {
      setData(null);
      setStatus("idle");
      return;
    }
    setStatus("loading");
    setError(null);
    api
      .getReview(reviewId)
      .then((res) => {
        setData(res);
        setStatus("idle");
      })
      .catch((e: Error) => {
        setError(e.message);
        setStatus("error");
      });
  }, [reviewId]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading: status === "loading", error, refetch };
}
