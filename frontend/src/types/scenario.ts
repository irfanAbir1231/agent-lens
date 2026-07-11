import type { ISODateTime } from "./common";

export type ScenarioStatus = "AVAILABLE" | "ACTIVE";

export interface Scenario {
  scenarioId: string;
  name: string;
  description: string;
  status: ScenarioStatus;
  activatedAt: ISODateTime | null;
}
