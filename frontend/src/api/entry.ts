// frontend/src/api/entry.ts
import { createRequest } from "./http";

const request = createRequest("/api/entry");

export type EntryResult =
  | { decision: "insert"; property_id: number }
  | { decision: "review"; candidate_property_id: number | null }
  | { decision: "discard" };

export function enterPost(rowId: number): Promise<EntryResult> {
  return request(`/${rowId}`, { method: "POST" });
}
