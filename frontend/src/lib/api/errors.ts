export type FrontendApiErrorCode = "NOT_FOUND" | "INVALID_REQUEST" | "DATA_QUALITY_BLOCKED" | "UNAVAILABLE" | "TIMEOUT" | "UNAUTHORIZED" | "FORBIDDEN" | "VALIDATION_FAILED" | "UNEXPECTED_RESPONSE";

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

export function apiErrorFromStatus(status:number,message?:string):FrontendApiError { const table:Record<number,{code:FrontendApiErrorCode;message:string}>={400:{code:"INVALID_REQUEST",message:"The request was invalid."},401:{code:"UNAUTHORIZED",message:"Sign in is required."},403:{code:"FORBIDDEN",message:"You do not have access to this action."},404:{code:"NOT_FOUND",message:"The requested resource was not found."},422:{code:"VALIDATION_FAILED",message:"The submitted data failed validation."}}; const item=table[status]??{code:"UNAVAILABLE" as const,message:"The backend is currently unavailable."}; return new FrontendApiError(item.code,message??item.message,status) }

export function notFound(resource: string, id: string): FrontendApiError {
  return new FrontendApiError("NOT_FOUND", `${resource} '${id}' was not found.`, 404);
}
