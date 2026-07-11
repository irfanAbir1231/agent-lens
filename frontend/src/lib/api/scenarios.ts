import { defaultScenarioId, scenarios } from "@/mocks";
import type { Scenario } from "@/types";
import { findMockOrThrow, mockResponse } from "./mock-client";
import { mockDelay } from "./mock-delay";

let activeScenarioId = defaultScenarioId;
export interface ScenarioPreset { id:string; name:string; description:string; conditions:string[]; response:string; provider:"BKASH"|"NAGAD"|"ROCKET"; delay:number; demand:number; blocked:boolean }
export const scenarioPresets: ScenarioPreset[] = [
  {id:"normal",name:"Normal Day",description:"Expected demand and healthy feeds.",conditions:["Demand at baseline","Healthy provider feeds"],response:"No alert; monitoring continues",provider:"NAGAD",delay:0,demand:1,blocked:false},
  {id:"eid",name:"Eid Demand Spike",description:"Expected seasonal demand increases.",conditions:["Eid context","Demand 2.7x normal"],response:"Context-aware review",provider:"NAGAD",delay:0,demand:2.7,blocked:false},
  {id:"shortage",name:"Hidden Provider Shortage",description:"Liquidity pressure emerges behind transaction activity.",conditions:["Cash-out 2.7x normal","Cash-in below baseline","Physical cash declining","Repeated near-identical transactions"],response:"Critical pressure and human review",provider:"NAGAD",delay:0,demand:2.7,blocked:false},
  {id:"repeated",name:"Repeated Transactions",description:"Near-identical transactions require context.",conditions:["Repeated amounts enabled"],response:"Unusual activity requires review",provider:"NAGAD",delay:0,demand:1.8,blocked:false},
  {id:"delayed",name:"Delayed Provider Feed",description:"Stale Rocket data blocks advice.",conditions:["Feed delayed 22 minutes"],response:"Manual verification required",provider:"ROCKET",delay:22,demand:1,blocked:true},
  {id:"conflict",name:"Conflicting Balance",description:"Conflicting records lower confidence.",conditions:["Balance sources disagree"],response:"Analysis limited pending verification",provider:"BKASH",delay:0,demand:1,blocked:true},
  {id:"response",name:"Coordinated Response",description:"Verified support stabilizes pressure.",conditions:["Agent contacted","Provider operations assigned"],response:"Continue monitored recovery",provider:"NAGAD",delay:0,demand:1.3,blocked:false},
];
export function getScenarioPresets(): Promise<ScenarioPreset[]> { return mockResponse(scenarioPresets); }

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
