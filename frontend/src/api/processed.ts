// frontend/src/api/processed.ts
import type { PostWithNav, AuthorPosts } from "./posts";

const BASE = "/api/processed";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export function getNextProcessed(): Promise<{ row_id: number | null }> {
  return request("/next");
}

export function getProcessedPost(rowId: number): Promise<PostWithNav> {
  return request(`/${rowId}`);
}

export function getAuthorProcessedPosts(rowId: number): Promise<AuthorPosts> {
  return request(`/author/${rowId}`);
}
