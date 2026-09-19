// frontend/src/api/processed.ts
import type { PostWithNav, AuthorPosts } from "./posts";
import { createRequest } from "./http";

const request = createRequest("/api/processed");

export function getNextProcessed(): Promise<{ row_id: number | null }> {
  return request("/next");
}

export function getProcessedPost(rowId: number): Promise<PostWithNav> {
  return request(`/${rowId}`);
}

export function getAuthorProcessedPosts(rowId: number): Promise<AuthorPosts> {
  return request(`/author/${rowId}`);
}
