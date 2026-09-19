// frontend/src/api/admin.ts
import { createRequest } from "./http";

const request = createRequest("/api/admin");

export interface BlacklistRow {
  author: string;
  count: number;
}

export interface FilterRow {
  phrase: string;
  added_at: string | null;
}

export function getBlacklist(
  sort: "count" | "alpha" = "count",
): Promise<{ rows: BlacklistRow[] }> {
  return request(`/blacklist?sort=${sort}`);
}

export function addBlacklist(
  author: string,
): Promise<{ ok: boolean; inserted: boolean; skipped: number }> {
  return request("/blacklist", {
    method: "POST",
    body: JSON.stringify({ author }),
  });
}

export function deleteBlacklist(author: string): Promise<{ ok: boolean }> {
  return request("/blacklist", {
    method: "DELETE",
    body: JSON.stringify({ author }),
  });
}

export function getFilters(): Promise<{ rows: FilterRow[] }> {
  return request("/filters");
}

export function addFilterPhrase(
  phrase: string,
): Promise<{ ok: boolean; already_exists: boolean }> {
  return request("/filters", {
    method: "POST",
    body: JSON.stringify({ phrase }),
  });
}

export function deleteFilterPhrase(phrase: string): Promise<{ ok: boolean }> {
  return request("/filters", {
    method: "DELETE",
    body: JSON.stringify({ phrase }),
  });
}
