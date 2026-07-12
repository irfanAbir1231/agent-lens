import { getActiveActor } from "./actor";
import { apiConfig } from "./config";
import { apiErrorFromStatus, FrontendApiError } from "./errors";

type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

const isJsonValue = (value: unknown): value is JsonValue => value === null
  || ["string", "number", "boolean"].includes(typeof value)
  || Array.isArray(value) && value.every(isJsonValue)
  || typeof value === "object" && Object.values(value as Record<string, unknown>).every(isJsonValue);

function errorMessage(value: unknown): string | undefined {
  if (typeof value !== "object" || value === null) return undefined;
  const record = value as Record<string, unknown>;
  return typeof record.message === "string" ? record.message : typeof record.detail === "string" ? record.detail : undefined;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), apiConfig.timeoutMilliseconds);
  try {
    const actorId = await getActiveActor();
    const response = await fetch(`${apiConfig.baseUrl}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { Accept: "application/json", "X-Actor-ID": actorId, ...(init.body ? { "Content-Type": "application/json" } : {}), ...init.headers },
      // This is a live operational dashboard, not static content: Next.js's
      // fetch patching defaults an unspecified `cache` to "force-cache" for
      // GET requests, which would silently serve a stale snapshot from
      // whenever a route was first rendered instead of current backend
      // state. Every request must be fresh.
      cache: "no-store",
    });
    const body: unknown = await response.json().catch(() => null);
    if (!response.ok) throw apiErrorFromStatus(response.status, errorMessage(body));
    if (!isJsonValue(body)) throw new FrontendApiError("UNEXPECTED_RESPONSE", "The server returned an unexpected response.", 502);
    return body as T;
  } catch (error) {
    if (error instanceof FrontendApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") throw new FrontendApiError("TIMEOUT", "The request timed out. Try again.", 408);
    throw new FrontendApiError("UNAVAILABLE", "The backend is unavailable. Continue in mock mode or retry later.", 503);
  } finally {
    clearTimeout(timer);
  }
}

export const httpClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: JsonValue, headers?: HeadersInit) => request<T>(path, { method: "POST", body: JSON.stringify(body), headers, cache: "no-store" }),
};
