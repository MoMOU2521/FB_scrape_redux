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

export interface GroupStatRow {
  group_name: string;
  total: number;
  selected: number;
  rate: number;
}

export interface StatsResponse {
  groups: GroupStatRow[];
  total_posts: number;
  total_selected: number;
  total_rate: number;
}

export interface AuthorRow {
  author: string;
  count: number;
  first_unprocessed_id: number;
}

export interface BuildingOption {
  id: number;
  name: string;
}

export function getStats(): Promise<StatsResponse> {
  return request("/stats");
}

export function getAuthors(minCount = 2): Promise<{ rows: AuthorRow[] }> {
  return request(`/authors?min_count=${minCount}`);
}

export function getBuildings(): Promise<{ buildings: BuildingOption[] }> {
  return request("/buildings");
}

export function addAlias(
  buildingId: number,
  alias: string,
): Promise<{ ok: boolean }> {
  return request("/add-alias", {
    method: "POST",
    body: JSON.stringify({ building_id: buildingId, alias }),
  });
}
