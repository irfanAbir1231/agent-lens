export type ApiMode = "mock" | "fastapi";

// The adapter will support "fastapi" when the backend contract is connected.
export const apiMode: ApiMode = "mock";

export const apiConfig = {
  mode: apiMode,
  mockDelayMilliseconds: 120,
} as const;
