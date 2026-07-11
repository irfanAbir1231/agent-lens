import type { AmountMinor, ISODateTime, ProviderId } from "./common";

export type TransactionType = "CASH_IN" | "CASH_OUT";
export type TransactionStatus = "SUCCESS" | "FAILED" | "PENDING";

export interface Transaction {
  transactionId: string;
  agentId: string;
  providerId: ProviderId;
  transactionType: TransactionType;
  amountMinor: AmountMinor;
  status: TransactionStatus;
  occurredAt: ISODateTime;
  syntheticAccountId: string;
}
