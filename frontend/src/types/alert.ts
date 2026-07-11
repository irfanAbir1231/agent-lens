import type { AlertStatus, Confidence, ISODateTime, ProviderId, Severity } from "./common";
import type { AnomalyEvidence } from "./anomaly";
import type { AlertType } from "./risk";

export interface Alert {
  alertId: string;
  agentId: string;
  providerId: ProviderId;
  title: string;
  alertType: AlertType;
  severity: Severity;
  confidence: Confidence;
  status: AlertStatus;
  summary: string;
  disclaimer: string;
  evidence: AnomalyEvidence[];
  possibleLegitimateExplanations: string[];
  limitations: string[];
  createdAt: ISODateTime;
}
