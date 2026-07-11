import type { ISODateTime } from "./common";
import type { AIAdvisory } from "./advisory";
import type { AnomalyResult } from "./anomaly";
import type { DataQualityResult } from "./data-quality";
import type { LiquidityForecast } from "./forecast";
import type { RiskAssessment } from "./risk";

export interface AgentAnalysis {
  analysisId: string;
  agentId: string;
  dataQuality: DataQualityResult[];
  forecasts: LiquidityForecast[];
  anomalyResult: AnomalyResult;
  riskAssessment: RiskAssessment;
  advisory: AIAdvisory;
  alertId: string;
  caseId: string | null;
  calculatedAt: ISODateTime;
}

export interface RunAnalysisOptions {
  scenarioId?: string;
  forceRefresh?: boolean;
}
