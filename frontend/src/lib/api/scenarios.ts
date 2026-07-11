import { defaultScenarioId, scenarios } from "@/mocks";
import type { Scenario } from "@/types";
import { findMockOrThrow, mockResponse } from "./mock-client";
import { mockDelay } from "./mock-delay";

let activeScenarioId = defaultScenarioId;

function currentScenarios(): Scenario[] {
  return scenarios.map((scenario) => ({
    ...scenario,
    status: scenario.scenarioId === activeScenarioId ? "ACTIVE" : "AVAILABLE",
    activatedAt: scenario.scenarioId === activeScenarioId ? scenario.activatedAt ?? "2026-07-11T08:42:00Z" : null,
  }));
}

export function getScenarios(): Promise<Scenario[]> {
  return mockResponse(currentScenarios());
}

export async function activateScenario(scenarioId: string): Promise<Scenario> {
  await mockDelay();
  findMockOrThrow(scenarios, (scenario) => scenario.scenarioId === scenarioId, "Scenario", scenarioId);
  activeScenarioId = scenarioId;
  return findMockOrThrow(currentScenarios(), (scenario) => scenario.scenarioId === scenarioId, "Scenario", scenarioId);
}

export function resetScenario(): Promise<Scenario> {
  activeScenarioId = defaultScenarioId;
  return mockResponse(findMockOrThrow(currentScenarios(), (scenario) => scenario.scenarioId === defaultScenarioId, "Scenario", defaultScenarioId));
}
