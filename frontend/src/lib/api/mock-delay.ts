import { apiConfig } from "./config";

export function mockDelay(milliseconds = apiConfig.mockDelayMilliseconds): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}
