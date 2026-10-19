import { requestJson } from "./http";
import type { AppSettings, AppSettingsUpdate } from "./types";

/** GET /api/admin/settings -> current settings and the models to choose from (admin only) */
export function getSettings(): Promise<AppSettings> {
  return requestJson("/admin/settings");
}

/** PUT /api/admin/settings  { model, temperature } -> the saved settings (admin only) */
export function updateSettings(update: AppSettingsUpdate): Promise<AppSettings> {
  return requestJson("/admin/settings", { method: "PUT", body: update });
}
