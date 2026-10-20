import { clearSession, getAuthHeader } from "./session";

/**
 * Error carrying the HTTP status and the backend's `detail` message (English, for logs).
 * `code` and `params` identify the problem for localized display, see i18n/apiErrors.ts.
 */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly code?: string,
    readonly params?: Record<string, string | number>,
  ) {
    super(message);
  }
}

/**
 * `body` may be a FormData (sent as-is) or any JSON-serialisable value.
 * `redirectOnUnauthorized: false` lets the caller handle a 401 itself (the login form).
 */
type ApiInit = Omit<RequestInit, "body"> & { body?: unknown; redirectOnUnauthorized?: boolean };

let onUnauthorized: () => void = () => {};

/** Called after a 401 has cleared the session, e.g. to navigate to the login page. */
export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

/** fetch wrapper for the REST backend, authenticating with the stored HTTP Basic header. */
export async function request(path: string, init: ApiInit = {}): Promise<Response> {
  const { body, headers, redirectOnUnauthorized = true, ...rest } = init;
  const isJson = body !== undefined && !(body instanceof FormData);
  const auth = getAuthHeader();
  const response = await fetch(`/api${path}`, {
    ...rest,
    body: isJson ? JSON.stringify(body) : (body as FormData | undefined),
    headers: {
      ...(auth && { Authorization: auth }),
      ...(isJson && { "Content-Type": "application/json" }),
      ...headers,
    },
  });
  if (!response.ok) {
    if (response.status === 401 && redirectOnUnauthorized) {
      clearSession();
      onUnauthorized();
    }
    const body = await response.json().then((d) => d, () => undefined);
    const detail = body?.detail;
    throw new ApiError(
      response.status,
      typeof detail === "string" ? detail : response.statusText,
      typeof body?.code === "string" ? body.code : undefined,
      body?.params,
    );
  }
  return response;
}

export async function requestJson<T>(path: string, init?: ApiInit): Promise<T> {
  return (await request(path, init)).json();
}
