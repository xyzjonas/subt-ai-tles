const KEY = "auth";

/** `Authorization` header value for HTTP Basic (UTF-8 safe, as the backend expects). */
export function basicHeader(username: string, password: string): string {
  const bytes = new TextEncoder().encode(`${username}:${password}`);
  return `Basic ${btoa(String.fromCharCode(...bytes))}`;
}

export const getAuthHeader = () => sessionStorage.getItem(KEY);
export const isSignedIn = () => getAuthHeader() !== null;
export const saveSession = (header: string) => sessionStorage.setItem(KEY, header);
export const clearSession = () => sessionStorage.removeItem(KEY);
