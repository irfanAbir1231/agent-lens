import { httpClient, type JsonValue } from "./http-client";

const id = (value: string) => encodeURIComponent(value);

export const fastApiClient = {
  health: <T>() => httpClient.get<T>("/api/v1/health"),
  overview: <T>() => httpClient.get<T>("/api/v1/overview"),
  agents: <T>() => httpClient.get<T>("/api/v1/agents?page_size=100"),
  agent: <T>(agentId: string) => httpClient.get<T>(`/api/v1/agents/${id(agentId)}`),
  forecast: <T>(agentId: string) => httpClient.get<T>(`/api/v1/agents/${id(agentId)}/forecast`),
  analyze: <T>(agentId: string, key: string) => httpClient.post<T>(`/api/v1/agents/${id(agentId)}/analysis`, {}, { "Idempotency-Key": key }),
  alerts: <T>() => httpClient.get<T>("/api/v1/alerts?page_size=100"),
  alert: <T>(alertId: string) => httpClient.get<T>(`/api/v1/alerts/${id(alertId)}`),
  cases: <T>() => httpClient.get<T>("/api/v1/cases?page_size=100"),
  case: <T>(caseId: string) => httpClient.get<T>(`/api/v1/cases/${id(caseId)}`),
  caseAction: <T>(caseId: string, action: string, body: JsonValue) => httpClient.post<T>(`/api/v1/cases/${id(caseId)}/${action}`, body),
  dataQuality: <T>() => httpClient.get<T>("/api/v1/data-quality?page_size=100"),
  metrics: <T>() => httpClient.get<T>("/api/v1/metrics"),
  auditEvents: <T>() => httpClient.get<T>("/api/v1/audit-events?page_size=100"),
  scenarios: <T>() => httpClient.get<T>("/api/v1/scenarios"),
  activateScenario: <T>(scenarioId: string) => httpClient.post<T>(`/api/v1/scenarios/${id(scenarioId)}/activate`, {}),
};
