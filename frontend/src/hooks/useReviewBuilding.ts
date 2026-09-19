// frontend/src/hooks/useReviewBuilding.ts
import { useCallback, useEffect, useState } from "react";
import * as api from "@/api/reviewBuilding";
import type { BuildingReviewWithNav } from "@/api/reviewBuilding";

type Status = "idle" | "loading" | "error";

export function useReviewBuilding(postId: number | null) {
  const [data, setData] = useState<BuildingReviewWithNav | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(() => {
    if (postId == null) {
      setData(null);
      setStatus("idle");
      return;
    }
    setStatus("loading");
    setError(null);
    api
      .getBuildingReview(postId)
      .then((res) => {
        setData(res);
        setStatus("idle");
      })
      .catch((e: Error) => {
        setError(e.message);
        setStatus("error");
      });
  }, [postId]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading: status === "loading", error, refetch };
}
