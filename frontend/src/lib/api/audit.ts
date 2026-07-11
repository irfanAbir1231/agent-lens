import { auditEvents } from "@/mocks";
import type { AuditEvent } from "@/types";
import { mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { AuditListDto } from "./backend-dto";

export async function getAuditEvents(): Promise<AuditEvent[]> {
  if (apiConfig.mode === "mock") return mockResponse(auditEvents);
  const response = await fastApiClient.auditEvents<AuditListDto>();
  return response.events.map((item) => ({ auditEventId: item.id, eventType: item.action as AuditEvent["eventType"], occurredAt: item.created_at, actorName: item.actor_id ?? "System", actorRole: (item.actor_role ?? "SYSTEM_ADMIN") as AuditEvent["actorRole"], resourceType: item.case_id ? "CASE" : item.alert_id ? "ALERT" : item.analysis_id ? "ANALYSIS" : "SCENARIO", resourceId: item.case_id ?? item.alert_id ?? item.analysis_id ?? item.id, summary: item.action.replaceAll("_", " ") }));
}
export interface AuditRow { id:string;time:string;timestamp:string;actor:string;role:string;action:string;provider:string;resource:string;previous:string;next:string;reason:string;synthetic:boolean }
const auditRows:AuditRow[]=[
 {id:"AUDIT-2039",time:"2:35 PM",timestamp:"2026-07-11T08:35:00Z",actor:"System",role:"ANALYSIS_PIPELINE",action:"Alert created",provider:"Nagad",resource:"ALT-2039",previous:"-",next:"NEW",reason:"Critical liquidity forecast",synthetic:true},
 {id:"AUDIT-8017-A",time:"2:38 PM",timestamp:"2026-07-11T08:38:00Z",actor:"Operations Officer",role:"PROVIDER_OPERATIONS",action:"Case assigned",provider:"Nagad",resource:"CASE-8017",previous:"NEW",next:"ASSIGNED",reason:"Field verification required",synthetic:true},
 {id:"AUDIT-8017-B",time:"2:39 PM",timestamp:"2026-07-11T08:39:00Z",actor:"Field Officer 12",role:"FIELD_OFFICER",action:"Case acknowledged",provider:"Nagad",resource:"CASE-8017",previous:"ASSIGNED",next:"ACKNOWLEDGED",reason:"Assignment accepted",synthetic:true},
 {id:"AUDIT-8017-C",time:"2:44 PM",timestamp:"2026-07-11T08:44:00Z",actor:"Field Officer 12",role:"FIELD_OFFICER",action:"Case escalated",provider:"Nagad",resource:"CASE-8017",previous:"UNDER_REVIEW",next:"ESCALATED",reason:"Repeated amounts remain unexplained",synthetic:true},
];
export async function getAuditRows():Promise<AuditRow[]>{
 if(apiConfig.mode==="mock") return mockResponse(auditRows);
 const response=await fastApiClient.auditEvents<AuditListDto>();
 return response.events.map(item=>({id:item.id,time:new Date(item.created_at).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}),timestamp:item.created_at,actor:item.actor_id??"System",role:item.actor_role??"SYSTEM",action:item.action.replaceAll("_"," "),provider:String(item.metadata.provider??"-"),resource:item.case_id??item.alert_id??item.analysis_id??item.id,previous:item.before_status??"-",next:item.after_status??"-",reason:String(item.metadata.reason??"Recorded by backend"),synthetic:true}));
}
