// frontend/src/api/admin.ts
import { createRequest } from "./http";

const request = createRequest("/api/admin");

export function addBlacklist(
  author: string,
): Promise<{ ok: boolean; inserted: boolean; skipped: number }> {
  return request("/blacklist", {
    method: "POST",
    body: JSON.stringify({ author }),
  });
}

export function addFilterPhrase(
  phrase: string,
): Promise<{ ok: boolean; already_exists: boolean }> {
  return request("/filters", {
    method: "POST",
    body: JSON.stringify({ phrase }),
  });
}
