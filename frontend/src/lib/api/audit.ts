import { auditEvents } from "@/mocks";
import type { AuditEvent } from "@/types";
import { mockResponse } from "./mock-client";

export function getAuditEvents(): Promise<AuditEvent[]> {
  return mockResponse(auditEvents);
}
export interface AuditRow { id:string;time:string;timestamp:string;actor:string;role:string;action:string;provider:string;resource:string;previous:string;next:string;reason:string;synthetic:boolean }
const auditRows:AuditRow[]=[
 {id:"AUDIT-2039",time:"2:35 PM",timestamp:"2026-07-11T08:35:00Z",actor:"System",role:"ANALYSIS_PIPELINE",action:"Alert created",provider:"Nagad",resource:"ALT-2039",previous:"-",next:"NEW",reason:"Critical liquidity forecast",synthetic:true},
 {id:"AUDIT-8017-A",time:"2:38 PM",timestamp:"2026-07-11T08:38:00Z",actor:"Operations Officer",role:"PROVIDER_OPERATIONS",action:"Case assigned",provider:"Nagad",resource:"CASE-8017",previous:"NEW",next:"ASSIGNED",reason:"Field verification required",synthetic:true},
 {id:"AUDIT-8017-B",time:"2:39 PM",timestamp:"2026-07-11T08:39:00Z",actor:"Field Officer 12",role:"FIELD_OFFICER",action:"Case acknowledged",provider:"Nagad",resource:"CASE-8017",previous:"ASSIGNED",next:"ACKNOWLEDGED",reason:"Assignment accepted",synthetic:true},
 {id:"AUDIT-8017-C",time:"2:44 PM",timestamp:"2026-07-11T08:44:00Z",actor:"Field Officer 12",role:"FIELD_OFFICER",action:"Case escalated",provider:"Nagad",resource:"CASE-8017",previous:"UNDER_REVIEW",next:"ESCALATED",reason:"Repeated amounts remain unexplained",synthetic:true},
];
export function getAuditRows():Promise<AuditRow[]>{return mockResponse(auditRows)}
