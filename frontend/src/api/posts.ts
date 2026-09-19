// frontend/src/api/posts.ts
import { createRequest } from "./http";

const request = createRequest("/api/posts");

export interface Post {
  id: number;
  post_id: string;
  author: string;
  text: string;
  post_url: string;
  processed: number;
  group_name: string;
  scraped_at: string;
  selected: number;
  result_json_v1: string | null;
  gate1_reasoning: string | null;
  gate1_prompt_version: string | null;
  extraction_result_json: string | null;
  extraction_reasoning: string | null;
  extraction_prompt_version: string | null;
  unprocessed_count: number;
}

export interface NavContext {
  current: number;
  total: number;
  prev_id: number | null;
  next_id: number | null;
}

export interface PostWithNav {
  post: Post;
  nav: NavContext;
}

export interface AuthorPosts {
  author: string;
  post: Post | null;
  nav: NavContext | null;
}

export function getNextUnprocessed(): Promise<{ row_id: number | null }> {
  return request("/next");
}

export function getPost(rowId: number): Promise<PostWithNav> {
  return request(`/${rowId}`);
}

export function getAuthorPosts(rowId: number): Promise<AuthorPosts> {
  return request(`/author/${rowId}`);
}

export function markProcessed(
  rowId: number,
  processed: 0 | 1,
): Promise<{ ok: boolean }> {
  return request(`/${rowId}/mark`, {
    method: "POST",
    body: JSON.stringify({ processed }),
  });
}

export function toggleSelected(
  rowId: number,
  selected: 0 | 1,
): Promise<{ ok: boolean }> {
  return request(`/${rowId}/selected`, {
    method: "POST",
    body: JSON.stringify({ selected }),
  });
}

export function deletePost(rowId: number): Promise<{ ok: boolean }> {
  return request(`/${rowId}`, { method: "DELETE" });
}
