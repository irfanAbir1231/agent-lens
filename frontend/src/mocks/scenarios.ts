import type { Scenario } from "@/types";

export const defaultScenarioId = "SCENARIO-EID-RUSH";

export const scenarios: Scenario[] = [
  { scenarioId: defaultScenarioId, name: "Eid Rush", description: "High Nagad demand, unusual repeated amounts, and a delayed Rocket feed.", status: "ACTIVE", activatedAt: "2026-07-11T08:20:00Z" },
  { scenarioId: "SCENARIO-NORMAL-DAY", name: "Normal Day", description: "Expected provider demand with healthy data feeds.", status: "AVAILABLE", activatedAt: null },
  { scenarioId: "SCENARIO-CONFLICTING-BALANCE", name: "Conflicting Balance", description: "A provider balance inconsistency that blocks analysis.", status: "AVAILABLE", activatedAt: null },
];
