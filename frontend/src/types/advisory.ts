import type { AIAdvisoryStatus, SourceReference, UserRole } from "./common";

export interface AdvisoryAction {
  rank: number;
  title: string;
  description: string;
  responsibleRole: UserRole;
  requiresHumanApproval: true;
  sourceIds: string[];
}

export interface AIAdvisory {
  advisoryStatus: AIAdvisoryStatus;
  summary: string;
  operationalAssessment: string;
  why: string[];
  recommendedActions: AdvisoryAction[];
  uncertainty: string[];
  humanVerificationQuestions: string[];
  sourceReferences: SourceReference[];
  requiresHumanReview: true;
  prohibitedActionsConfirmed: boolean;
  disclaimer: string;
}
