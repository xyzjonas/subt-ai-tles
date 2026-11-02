import { request, requestJson } from "./http";
import type { Folder } from "./types";

/** GET /api/folders */
export function listFolders(): Promise<Folder[]> {
  return requestJson("/folders");
}

/** POST /api/folders  { name } -> 201 the created folder */
export function createFolder(name: string): Promise<Folder> {
  return requestJson("/folders", { method: "POST", body: { name } });
}

/** PATCH /api/folders/:id  { name } */
export function renameFolder(id: string, name: string): Promise<Folder> {
  return requestJson(`/folders/${id}`, { method: "PATCH", body: { name } });
}

/** DELETE /api/folders/:id — its requests are kept, just ungrouped */
export async function deleteFolder(id: string): Promise<void> {
  await request(`/folders/${id}`, { method: "DELETE" });
}
