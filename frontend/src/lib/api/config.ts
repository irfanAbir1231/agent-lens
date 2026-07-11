export type ApiMode = "mock" | "fastapi";
const configuredMode = process.env.NEXT_PUBLIC_API_MODE;
export const apiMode: ApiMode = configuredMode === "fastapi" ? "fastapi" : "mock";

export const apiConfig = {
  mode: apiMode,
  mockDelayMilliseconds: 120,
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  timeoutMilliseconds: 10_000,
} as const;
