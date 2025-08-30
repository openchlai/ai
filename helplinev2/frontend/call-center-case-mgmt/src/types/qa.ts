export interface QAEvaluation {
  id: number;
  counselorId: number;
  counselorName: string;
  supervisorId: number;
  supervisorName: string;
  score: number;
  callsEvaluated: number;
  talkTime: string;
  notes?: string;
  date: Date | string;
} 