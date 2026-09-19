// frontend/src/api/review.ts
import { createRequest } from "./http";

const request = createRequest("/api/review");

export interface ReviewRow {
  review_id: number;
  post_id: number;
  candidate_property_id: number | null;
  reviewed: number;
  created_at: string;
  author: string;
  fb_post_id: string;
  post_url: string;
  text: string;
  scraped_at: string;
  extraction_result_json: string;
}

export interface NavContext {
  current: number;
  total: number;
  prev_id: number | null;
  next_id: number | null;
}

export interface ReviewWithNav {
  row: ReviewRow;
  nav: NavContext;
}

export function getNextReview(): Promise<{ row_id: number | null }> {
  return request("/next");
}

export function getReview(reviewId: number): Promise<ReviewWithNav> {
  return request(`/${reviewId}`);
}

export function approveReview(
  reviewId: number,
): Promise<{ ok: boolean; property_id: number | null }> {
  return request(`/${reviewId}/approve`, { method: "POST" });
}

export function rejectReview(reviewId: number): Promise<{ ok: boolean }> {
  return request(`/${reviewId}/reject`, { method: "POST" });
}

export function dismissReview(reviewId: number): Promise<{ ok: boolean }> {
  return request(`/${reviewId}/dismiss`, { method: "POST" });
}
