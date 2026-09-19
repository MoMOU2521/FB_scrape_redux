// frontend/src/api/reviewBuilding.ts
import type { Post } from "./posts";
import { createRequest } from "./http";

const request = createRequest("/api/review-building");

export interface BuildingOption {
  id: number;
  name: string;
}

export interface NavContext {
  current: number;
  total: number;
  prev_id: number | null;
  next_id: number | null;
}

export interface BuildingReviewWithNav {
  post: Post;
  nav: NavContext;
  buildings: BuildingOption[];
}

export function getNextBuildingReview(): Promise<{ row_id: number | null }> {
  return request("/next");
}

export function getBuildingReview(
  postId: number,
): Promise<BuildingReviewWithNav> {
  return request(`/${postId}`);
}

export type EnterBuildingResult =
  | { ok: true; property_id: number | null }
  | { ok: true; sent_to_review: true; candidate_property_id: number | null }
  | { ok: true; discarded: true };

export function enterBuilding(postId: number): Promise<EnterBuildingResult> {
  return request(`/${postId}/enter`, { method: "POST" });
}

export function assignBuilding(
  postId: number,
  buildingId: number,
): Promise<{ ok: boolean; property_id: number | null }> {
  return request(`/${postId}/assign`, {
    method: "POST",
    body: JSON.stringify({ building_id: buildingId }),
  });
}

export function dismissBuildingReview(
  postId: number,
): Promise<{ ok: boolean }> {
  return request(`/${postId}/dismiss`, { method: "POST" });
}
