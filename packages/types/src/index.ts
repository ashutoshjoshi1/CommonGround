export type ConfidenceLabel = "high" | "review" | "low";

export interface UserSummary {
  id: string;
  email: string;
  full_name: string;
  is_admin: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  created_by_id: string;
  created_at: string;
  updated_at: string;
}

export interface Source {
  id: string;
  workspace_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  file_hash: string;
  status: string;
  metadata_json: Record<string, unknown>;
  dedupe_hint?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  citation_label: string;
  source_id: string;
  source_name: string;
  chunk_id: string;
  rank: number;
  score: number;
  excerpt: string;
}

export interface QueryResponse {
  run_id: string;
  answer: string;
  confidence_label: ConfidenceLabel;
  abstained: boolean;
  citations: Citation[];
  retrieved_passages: Citation[];
  prompt_version_id?: string | null;
  trace_summary: Record<string, unknown>;
}

export interface Run {
  id: string;
  workspace_id: string;
  query: string;
  answer?: string | null;
  status: string;
  confidence_label: ConfidenceLabel;
  abstained: boolean;
  provider?: string | null;
  model_name?: string | null;
  latency_ms?: number | null;
  created_at: string;
  completed_at?: string | null;
}

export interface Prompt {
  id: string;
  workspace_id: string;
  name: string;
  description?: string | null;
  is_archived: boolean;
  created_by_id: string;
  created_at: string;
  updated_at: string;
}

export interface PromptVersion {
  id: string;
  prompt_id: string;
  version_number: number;
  template: string;
  model_name: string;
  provider: string;
  settings_json: Record<string, unknown>;
  is_active: boolean;
  is_default: boolean;
  created_by_id: string;
  created_at: string;
}

export interface Evaluation {
  id: string;
  workspace_id: string;
  name: string;
  description?: string | null;
  status: string;
  prompt_version_id?: string | null;
  config_json: Record<string, unknown>;
  summary_json: Record<string, unknown>;
  created_by_id: string;
  created_at: string;
  completed_at?: string | null;
}

export interface AuditEvent {
  id: string;
  workspace_id?: string | null;
  user_id?: string | null;
  entity_type: string;
  entity_id?: string | null;
  action: string;
  details_json: Record<string, unknown>;
  created_at: string;
}
