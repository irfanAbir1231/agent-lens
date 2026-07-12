import type { DataHealthStatus, ProviderId } from "@/types";

export interface Page<T> { items: T[] }
export interface AgentDto {
  id: string; display_label: string; area: string; shared_cash_minor: number;
  provider_balances: { provider: ProviderId; provider_balance_minor: number; updated_at: string }[];
  feed_states: { provider: ProviderId; status: DataHealthStatus; last_received_at: string }[];
  recent_transactions?: TransactionDto[];
}
export interface TransactionDto { id: string; agent_id: string; provider: ProviderId; transaction_type: "CASH_IN" | "CASH_OUT"; amount_minor: number; status: "SUCCESS" | "FAILED" | "PENDING"; occurred_at: string; synthetic_account_reference: string }
export interface OverviewDto { generated_at: string; total_shared_cash_minor: number; provider_totals: { provider: ProviderId; total_provider_balance_minor: number }[]; feed_summary: { provider: ProviderId; status: DataHealthStatus; last_received_at: string | null }[] }
export interface ForecastDto {
  generated_at: string;
  data_quality_summary: { provider_results: { provider: ProviderId; confidence_multiplier: number }[] };
  provider_forecasts: {
    forecast_id: string; agent_id: string; provider: ProviderId; generated_at: string;
    current_balance_minor: number; predicted_net_outflow_minor: number;
    estimated_shortage_minutes: number | null; pressure_level: string; confidence: number;
    prediction_source: "XGBOOST_MODEL" | "DETERMINISTIC_FALLBACK"; model_version: string;
    top_factors: { code: string; label: string; effect: string }[];
  }[];
}
export interface AlertSummaryDto { id: string; agent_id: string; provider: ProviderId | null; alert_type: string; status: string; severity: string; confidence: number; created_at: string }
export interface AlertListDto { alerts: AlertSummaryDto[] }
export interface AlertDetailDto extends AlertSummaryDto { anomaly: { anomaly_score: number; review_level: string; evaluation_blocked: boolean; evidence: { code: string; description: string; measured_value: number }[]; legitimate_explanations: string[]; limitations: string[]; detector_version: string; data_window_end: string }; risk: { severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"; alert_type: "LIQUIDITY_PRESSURE" | "UNUSUAL_ACTIVITY" | "DATA_QUALITY" | "COMBINED_OPERATIONAL_REVIEW"; confidence: number; allow_ai_advisory: boolean; required_human_role: "AGENT" | "PROVIDER_OPERATIONS" | "FIELD_OFFICER" | "RISK_ANALYST" | "AREA_MANAGER" | "MANAGEMENT_VIEWER" | "SYSTEM_ADMIN"; allowed_actions: ("VERIFY_DEMAND" | "CONTACT_PROVIDER_OPERATIONS" | "COMPARE_CONTEXT" | "CONTINUE_MONITORING" | "ESCALATE_REVIEW")[]; prohibited_actions: string[]; rule_version: string; reasons: string[] }; limitations: string[] }
export interface CaseSummaryDto { id: string; alert_id: string; agent_id: string; status: string; severity: string; priority: number; assigned_to: string | null; latest_decision: string | null; created_at: string; version: number }
export interface CaseListDto { cases: CaseSummaryDto[] }
export interface CaseDetailDto extends CaseSummaryDto { timeline: { id: string; created_at: string; action: string; actor_id: string | null }[]; notes: { id: string; created_at: string; author_id: string; body: string }[]; capabilities: { can_acknowledge: boolean; can_add_note: boolean; can_decide: boolean; can_escalate: boolean; can_resolve: boolean } }
export interface MetricsDto { forecast: { mae_net_outflow_minor: number | null; rmse_net_outflow_minor: number | null; shortage_detection_lead_time_minutes: number | null }; anomaly: { precision: number | null; recall: number | null; f1: number | null; false_positive_rate: number | null }; ai: { validation_pass_count: number | null; completed_count: number | null; source_coverage_rate: number | null; one_call_compliance_rate: number | null; fallback_count: number | null; average_latency_ms: number | null }; workflow: { average_acknowledgement_seconds: number | null; average_resolution_seconds: number | null } }
export interface DataQualityDto { generated_at: string; results: { agent_id: string; provider_results: { provider: ProviderId; status: DataHealthStatus; confidence_multiplier: number; allow_forecast: boolean; allow_ai_advisory: boolean; component_scores: { freshness: number; completeness: number; consistency: number; validity: number }; issue_codes: string[]; issue_descriptions: string[]; recommended_verification_steps: string[] }[] }[] }
export interface AuditListDto { events: { id: string; action: string; actor_id: string | null; actor_role: string | null; case_id: string | null; alert_id: string | null; analysis_id: string | null; before_status: string | null; after_status: string | null; metadata: Record<string, string | number | boolean | null>; created_at: string }[] }
export interface AnalysisDto {
  analysis_id: string; agent_id: string; completed_at: string; alert_ids: string[];
  provider_results: { provider: ProviderId | null; alert: AlertDetailDto }[];
  advisory: { advisory_status: string; guidance: { summary: string; operational_assessment: string; why: string[]; recommended_actions: { rank: number; title: string; rationale: string; responsible_role: string; source_ids: string[] }[]; uncertainty: string[]; human_verification_questions: string[]; source_references: { source_id: string; relevance: string }[]; requires_human_review: true; prohibited_actions_confirmed: true } };
}
