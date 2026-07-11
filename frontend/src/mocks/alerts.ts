import type { Alert } from "@/types";
import { anomalyResult } from "./analyses";

export const alerts: Alert[] = [
  {
    alertId: "ALT-2039",
    agentId: "AGENT-104",
    providerId: "NAGAD",
    title: "Unusual Nagad cash-out activity requires review",
    alertType: "COMBINED_OPERATIONAL_REVIEW",
    severity: "HIGH",
    confidence: 0.82,
    status: "NEW",
    summary: "14 Nagad cash-out requests between BDT 9,800 and BDT 10,000 occurred within 12 minutes, above the recent simulated baseline.",
    disclaimer: "This is an operational risk signal, not proof of fraud.",
    evidence: anomalyResult.evidence,
    possibleLegitimateExplanations: anomalyResult.possibleLegitimateExplanations,
    limitations: anomalyResult.limitations,
    createdAt: "2026-07-11T08:35:00Z",
  },
];
