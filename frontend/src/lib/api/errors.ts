export type FrontendApiErrorCode = "NOT_FOUND" | "INVALID_REQUEST" | "DATA_QUALITY_BLOCKED" | "UNAVAILABLE";

export class FrontendApiError extends Error {
  readonly code: FrontendApiErrorCode;
  readonly status: number;

  constructor(code: FrontendApiErrorCode, message: string, status = 500) {
    super(message);
    this.name = "FrontendApiError";
    this.code = code;
    this.status = status;
  }
}

export function notFound(resource: string, id: string): FrontendApiError {
  return new FrontendApiError("NOT_FOUND", `${resource} '${id}' was not found.`, 404);
}
